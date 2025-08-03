#!/usr/bin/env node
/*
 * QiLife Duplicate Cleaner (Node.js)
 *
 * This script scans one or more directory trees and identifies duplicate
 * or nearly‑duplicate files based on file size, fuzzy name similarity and
 * a composite score.  Exact duplicates are detected via SHA‑256 checksums.
 *
 * Run with flags such as:
 *   node duplicateCleaner.js --roots "C:\path\to\scan,D:\other\path" --max-depth -1 --action report
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

function parseArgs(argv) {
  const args = {};
  for (let i = 2; i < argv.length; i++) {
    const arg = argv[i];
    if (arg.startsWith('--')) {
      const key = arg.substring(2);
      const value = argv[i + 1];
      args[key] = value;
      i++;
    }
  }
  return args;
}

async function walkDirectory(root, maxDepth = -1) {
  const results = [];
  async function helper(current, depth) {
    const entries = await fs.promises.readdir(current, { withFileTypes: true }).catch(() => []);
    for (const entry of entries) {
      const fullPath = path.join(current, entry.name);
      if (entry.isDirectory()) {
        if (maxDepth === -1 || depth < maxDepth) {
          await helper(fullPath, depth + 1);
        }
      } else if (entry.isFile()) {
        const stat = await fs.promises.stat(fullPath).catch(() => null);
        if (stat && stat.isFile()) {
          results.push({ path: fullPath, size: stat.size, name: entry.name, mtime: stat.mtimeMs });
        }
      }
    }
  }
  await helper(root, 0);
  return results;
}

function sha256(filePath) {
  return new Promise((resolve) => {
    const hash = crypto.createHash('sha256');
    const stream = fs.createReadStream(filePath);
    stream.on('error', () => resolve(null));
    stream.on('data', (chunk) => hash.update(chunk));
    stream.on('end', () => resolve(hash.digest('hex')));
  });
}

function normalizeName(name) {
  return name
    .replace(/\.[^.]+$/, '')
    .replace(/[^\w\s]/g, ' ')
    .replace(/\d{4}[-_]?(\d{2}[-_]?\d{2})?/, '')
    .toLowerCase()
    .trim()
    .replace(/\s+/g, ' ');
}

function levenshtein(a, b) {
  const la = a.length;
  const lb = b.length;
  if (la === 0) return lb;
  if (lb === 0) return la;
  let prevRow = new Array(lb + 1);
  let curRow = new Array(lb + 1);
  for (let j = 0; j <= lb; j++) prevRow[j] = j;
  for (let i = 1; i <= la; i++) {
    curRow[0] = i;
    for (let j = 1; j <= lb; j++) {
      const cost = a[i - 1] === b[j - 1] ? 0 : 1;
      curRow[j] = Math.min(curRow[j - 1] + 1, prevRow[j] + 1, prevRow[j - 1] + cost);
    }
    [prevRow, curRow] = [curRow, prevRow];
  }
  return prevRow[lb];
}

function similarity(a, b) {
  const maxLen = Math.max(a.length, b.length);
  if (maxLen === 0) return 1.0;
  const dist = levenshtein(a, b);
  return 1 - dist / maxLen;
}

function groupBySize(files) {
  const groups = new Map();
  for (const f of files) {
    const arr = groups.get(f.size) || [];
    arr.push(f);
    groups.set(f.size, arr);
  }
  return groups;
}

async function classifyGroup(group, thresholds, weights) {
  const results = [];
  const n = group.length;
  const normNames = group.map((f) => normalizeName(f.name));
  const hashes = {};
  async function getHash(idx) {
    if (!hashes[idx]) hashes[idx] = await sha256(group[idx].path);
    return hashes[idx];
  }
  for (let i = 0; i < n; i++) {
    for (let j = i + 1; j < n; j++) {
      const a = group[i];
      const b = group[j];
      const nameSim = similarity(normNames[i], normNames[j]);
      const sizeSim = a.size === 0 && b.size === 0 ? 1.0 : Math.min(a.size, b.size) / Math.max(a.size, b.size);
      const compSim = nameSim * weights.name + sizeSim * weights.size;
      let classification = 'IGNORE';
      let note = '';
      let hashA = null;
      let hashB = null;
      if (a.size === b.size || compSim >= thresholds.review) {
        hashA = await getHash(i);
        hashB = await getHash(j);
      }
      if (hashA && hashB && hashA === hashB) {
        classification = 'EXACT';
        note = 'Exact duplicate';
      } else if (compSim >= thresholds.ai && compSim < 1.0) {
        classification = 'AI_REVIEW';
        note = `Composite ${compSim.toFixed(3)} ≥ AI threshold ${thresholds.ai}`;
      } else if (compSim >= thresholds.prefer) {
        classification = 'PREFER_LARGER';
        note = `Composite ${compSim.toFixed(3)} ≥ Prefer threshold ${thresholds.prefer}`;
      } else if (compSim >= thresholds.review) {
        classification = 'MANUAL_REVIEW';
        note = `Composite ${compSim.toFixed(3)} ≥ Review threshold ${thresholds.review}`;
      }
      if (classification !== 'IGNORE') {
        results.push({ fileA: a, fileB: b, nameSim, sizeSim, compSim, classification, note });
      }
    }
  }
  return results;
}

function decideKeep(fileA, fileB, prefer = 'larger') {
  return prefer === 'larger' ? (fileA.size >= fileB.size ? fileA : fileB) : fileA;
}

async function handleFile(fileObj, classification, destRoot, action) {
  const relative = path.relative('/', fileObj.path).replace(/:/g, '');
  const targetDir = path.join(destRoot, classification);
  const destPath = path.join(targetDir, relative);
  await fs.promises.mkdir(path.dirname(destPath), { recursive: true });
  if (action === 'move' || action === 'link') {
    try {
      if (action === 'link') await fs.promises.link(fileObj.path, destPath);
      else await fs.promises.rename(fileObj.path, destPath);
    } catch {
      await fs.promises.copyFile(fileObj.path, destPath);
      if (action === 'move') await fs.promises.unlink(fileObj.path).catch(() => {});
    }
  } else if (action === 'delete') {
    await fs.promises.unlink(fileObj.path).catch(() => {});
  }
}

async function performActions(classifications, action, destRoot) {
  if (action === 'report') return;
  for (const item of classifications) {
    const { fileA, fileB, classification } = item;
    if (classification === 'EXACT' || classification === 'PREFER_LARGER') {
      const keep = decideKeep(fileA, fileB, 'larger');
      const discard = keep === fileA ? fileB : fileA;
      await handleFile(discard, classification, destRoot, action);
    } else if (classification === 'AI_REVIEW') {
      await handleFile(fileA, classification, destRoot, action);
      await handleFile(fileB, classification, destRoot, action);
    } else if (classification === 'MANUAL_REVIEW' && action !== 'report') {
      await handleFile(fileA, classification, destRoot, action);
      await handleFile(fileB, classification, destRoot, action);
    }
  }
}

async function writeReports(classifications, outputDir) {
  await fs.promises.mkdir(outputDir, { recursive: true });
  const csvLines = ['fileA,fileB,nameSim,sizeSim,composite,classification,note'];
  for (const item of classifications) {
    csvLines.push([
      item.fileA.path,
      item.fileB.path,"https://www.youtube.com/watch?v=SkBb-b18UNQ"
      item.nameSim.toFixed(3),
      item.sizeSim.toFixed(3),
      item.compSim.toFixed(3),
      item.classification,
      item.note.replace(/,/g, ';'),
    ].join(','));
  }
  await fs.promises.writeFile(path.join(outputDir, 'duplicates.csv'), csvLines.join('\n'), 'utf-8');
  await fs.promises.writeFile(path.join(outputDir, 'duplicates.json'), JSON.stringify(classifications, null, 2), 'utf-8');
}

async function main() {
  const args = parseArgs(process.argv);
  if (!args.roots) {
    console.error('Error: --roots parameter is required (comma‑separated paths)');
    process.exit(1);
  }
  const roots = args.roots.split(',').map((p) => p.trim()).filter(Boolean);
  const maxDepth = args['max-depth'] !== undefined ? parseInt(args['max-depth'], 10) : -1;
  const weightsArg = args.weights || '0.6,0.4';
  const [nameWStr, sizeWStr] = weightsArg.split(',');
  const weights = { name: parseFloat(nameWStr), size: parseFloat(sizeWStr) };
  const thresholds = {
    review: args['review-threshold'] !== undefined ? parseFloat(args['review-threshold']) : 0.90,
    prefer: args['prefer-threshold'] !== undefined ? parseFloat(args['prefer-threshold']) : 0.971,
    ai: args['ai-threshold'] !== undefined ? parseFloat(args['ai-threshold']) : 0.98,
  };
  const action = (args.action || 'report').toLowerCase();
  const outputDir = args.output || path.join(roots[0], '_DUPES');
  let allFiles = [];
  for (const root of roots) {
    const files = await walkDirectory(root, maxDepth);
    allFiles = allFiles.concat(files);
  }
  if (allFiles.length === 0) {
    console.log('No files found to process.');
    return;
  }
  const groups = groupBySize(allFiles);
  const classifications = [];
  for (const group of groups.values()) {
    if (group.length >= 2) {
      const classRes = await classifyGroup(group, thresholds, weights);
      classifications.push(...classRes);
    }
  }
  console.log(`Found ${classifications.length} candidate pairs across ${allFiles.length} files.`);
  await writeReports(classifications, outputDir);
  if (action !== 'report') {
    await performActions(classifications, action, outputDir);
    console.log(`Actions complete. See ${outputDir} for moved/linked files.`);
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
