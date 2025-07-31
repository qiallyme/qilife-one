// modules/fileflow/duplicate-cleaner.js
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const archiver = require('archiver');
const { promisify } = require('util');

const stat = promisify(fs.stat);
const readdir = promisify(fs.readdir);

// Hash file
async function hashFile(filePath) {
  return new Promise((resolve, reject) => {
    const hash = crypto.createHash('sha256');
    const stream = fs.createReadStream(filePath);
    stream.on('data', chunk => hash.update(chunk));
    stream.on('end', () => resolve(hash.digest('hex')));
    stream.on('error', reject);
  });
}

// Recursively walk directory with depth limit
async function walkDir(dir, depthLimit, currentDepth = 0, files = []) {
  if (currentDepth > depthLimit) return files;
  const entries = await readdir(dir, { withFileTypes: true });
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      await walkDir(fullPath, depthLimit, currentDepth + 1, files);
    } else {
      files.push(fullPath);
    }
  }
  return files;
}

// Find duplicates
async function findDuplicates(rootDir, depth = 3) {
  const files = await walkDir(rootDir, depth);
  const sizeMap = new Map();

  // Group by file size
  for (const file of files) {
    try {
      const stats = await stat(file);
      const size = stats.size;
      if (!sizeMap.has(size)) sizeMap.set(size, []);
      sizeMap.get(size).push(file);
    } catch (_) {}
  }

  // Filter size groups with >1
  const candidates = [...sizeMap.values()].filter(group => group.length > 1);

  // Hash and group
  const hashMap = new Map();
  for (const group of candidates) {
    for (const file of group) {
      const hash = await hashFile(file);
      if (!hashMap.has(hash)) hashMap.set(hash, []);
      hashMap.get(hash).push(file);
    }
  }

  // Return duplicates
  return [...hashMap.entries()].filter(([_, files]) => files.length > 1);
}

// Move duplicates to quarantine and zip
async function quarantineDuplicates(rootDir, duplicates) {
  const ts = new Date().toISOString().replace(/[:.]/g, '-');
  const quarantineDir = path.join(rootDir, `duplicates_pending_deletion_${ts}`);
  const zipPath = path.join(rootDir, `duplicate_backup_${ts}.zip`);

  fs.mkdirSync(quarantineDir, { recursive: true });

  // Create zip
  const output = fs.createWriteStream(zipPath);
  const archive = archiver('zip', { zlib: { level: 9 } });
  archive.pipe(output);

  for (const [hash, files] of duplicates) {
    const toMove = files.slice(1); // keep first
    for (const file of toMove) {
      const dest = path.join(quarantineDir, path.basename(file));
      fs.renameSync(file, dest);
      archive.file(dest, { name: path.basename(dest) });
    }
  }

  await archive.finalize();
  return { quarantineDir, zipPath };
}

module.exports = { findDuplicates, quarantineDuplicates };
