const fs = require('fs-extra');
const path = require('path');
const archiver = require('archiver');

async function createInstaller() {
  console.log('🔧 Creating installer package...');
  
  const installerPath = path.join(__dirname, '..', 'installer');
  const distPath = path.join(__dirname, '..', 'dist');
  const outputPath = path.join(__dirname, '..', 'dist', 'qilife-installer.zip');
  
  // Ensure directories exist
  await fs.ensureDir(installerPath);
  await fs.ensureDir(path.dirname(outputPath));
  
  // Copy necessary files to installer directory
  const filesToCopy = [
    { src: path.join(__dirname, '..', 'dist-electron'), dest: path.join(installerPath, 'electron-app') },
    { src: path.join(__dirname, '..', 'dist', 'python-backend.zip'), dest: path.join(installerPath, 'python-backend.zip') },
    { src: path.join(__dirname, 'install-instructions.md'), dest: path.join(installerPath, 'README.md') }
  ];
  
  for (const file of filesToCopy) {
    if (await fs.pathExists(file.src)) {
      await fs.copy(file.src, file.dest);
      console.log(`✅ Copied: ${path.basename(file.src)}`);
    } else {
      console.warn(`⚠️ File not found: ${file.src}`);
    }
  }
  
  // Create the installer zip
  const output = fs.createWriteStream(outputPath);
  const archive = archiver('zip', {
    zlib: { level: 9 }
  });
  
  output.on('close', () => {
    console.log(`✅ Installer created: ${archive.pointer()} total bytes`);
    console.log(`📦 Installer location: ${outputPath}`);
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
  archive.directory(installerPath, 'qilife-installer');
  
  await archive.finalize();
  
  console.log('🎉 Installer package complete!');
}

createInstaller().catch(console.error); 