const fs = require('fs-extra');
const path = require('path');
const archiver = require('archiver');

async function packageElectronManually() {
  console.log('📦 Packaging Electron app manually...');
  
  const electronAppPath = path.join(__dirname, '..', 'electron-app');
  const distPath = path.join(__dirname, '..', 'dist');
  const outputPath = path.join(__dirname, '..', 'dist', 'qilife-electron.zip');
  
  // Ensure dist directory exists
  await fs.ensureDir(path.dirname(outputPath));
  
  // Create a temporary directory for the electron app
  const tempDir = path.join(__dirname, '..', 'temp-electron');
  await fs.ensureDir(tempDir);
  
  // Copy electron app files
  await fs.copy(electronAppPath, path.join(tempDir, 'electron-app'));
  
  // Copy built dist files
  await fs.copy(distPath, path.join(tempDir, 'dist'));
  
  // Copy node_modules (only necessary ones)
  const nodeModulesPath = path.join(__dirname, '..', 'node_modules');
  const essentialModules = ['electron'];
  
  for (const module of essentialModules) {
    const modulePath = path.join(nodeModulesPath, module);
    if (await fs.pathExists(modulePath)) {
      await fs.copy(modulePath, path.join(tempDir, 'node_modules', module));
    }
  }
  
  // Copy package.json
  await fs.copy(
    path.join(__dirname, '..', 'package.json'),
    path.join(tempDir, 'package.json')
  );
  
  // Create the zip file
  const output = fs.createWriteStream(outputPath);
  const archive = archiver('zip', {
    zlib: { level: 9 }
  });
  
  output.on('close', () => {
    console.log(`✅ Electron app packaged: ${archive.pointer()} total bytes`);
    console.log(`📦 Location: ${outputPath}`);
  });
  
  archive.on('warning', (err) => {
    if (err.code === 'ENOENT') {
      console.warn('⚠️ Archive warning:', err);
    } else {
      throw err;
    }
  });
  
  archive.on('error', (err) => {
    throw err;
  });
  
  archive.pipe(output);
  archive.directory(tempDir, 'qilife-electron');
  
  await archive.finalize();
  
  // Clean up temp directory
  await fs.remove(tempDir);
  
  console.log('📦 Electron app packaging complete!');
}

packageElectronManually().catch(console.error); 