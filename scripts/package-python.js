const fs = require('fs-extra');
const path = require('path');
const archiver = require('archiver');

async function packagePythonBackend() {
  console.log('📦 Packaging Python backend...');
  
  const pythonBackendPath = path.join(__dirname, '..', 'python-backend');
  const outputPath = path.join(__dirname, '..', 'dist', 'python-backend.zip');
  
  // Ensure dist directory exists
  await fs.ensureDir(path.dirname(outputPath));
  
  // Create a write stream for the zip file
  const output = fs.createWriteStream(outputPath);
  const archive = archiver('zip', {
    zlib: { level: 9 } // Sets the compression level
  });
  
  // Listen for all archive data to be written
  output.on('close', () => {
    console.log(`✅ Python backend packaged: ${archive.pointer()} total bytes`);
  });
  
  // Good practice to catch warnings (ie stat failures and other non-blocking errors)
  archive.on('warning', (err) => {
    if (err.code === 'ENOENT') {
      console.warn('⚠️ Archive warning:', err);
    } else {
      throw err;
    }
  });
  
  // Good practice to catch this error explicitly
  archive.on('error', (err) => {
    throw err;
  });
  
  // Pipe archive data to the file
  archive.pipe(output);
  
  // Add the python-backend directory to the archive
  archive.directory(pythonBackendPath, 'python-backend');
  
  // Finalize the archive
  await archive.finalize();
  
  console.log('📦 Python backend packaging complete!');
}

packagePythonBackend().catch(console.error); 