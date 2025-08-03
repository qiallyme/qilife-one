const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
    },
  });
  
  // Try to load from the correct path - first check if dist exists in renderer
  const rendererPath = path.join(__dirname, '..', 'renderer', 'dist', 'index.html');
  const rootPath = path.join(__dirname, '..', '..', 'dist', 'index.html');
  
  // Check which path exists and load accordingly
  if (require('fs').existsSync(rendererPath)) {
    win.loadFile(rendererPath);
  } else if (require('fs').existsSync(rootPath)) {
    win.loadFile(rootPath);
  } else {
    // If neither exists, load the root index.html directly
    win.loadFile(path.join(__dirname, '..', '..', 'index.html'));
  }
}

app.whenReady().then(createWindow);
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

// IPC handler that invokes the duplicate cleaner script
ipcMain.handle('run-duplicate-cleaner', async (_event, options) => {
  const scriptPath = path.join(
    __dirname,
    '..',
    'modules',
    'fileflow',
    'duplicate_cleaner',
    'duplicateCleaner.js',
  );
  return new Promise((resolve, reject) => {
    const args = [];
    if (options.roots) args.push('--roots', options.roots.join(','));
    if (options.maxDepth !== undefined) args.push('--max-depth', String(options.maxDepth));
    if (options.weights) args.push('--weights', `${options.weights.name},${options.weights.size}`);
    if (options.reviewThreshold) args.push('--review-threshold', String(options.reviewThreshold));
    if (options.preferThreshold) args.push('--prefer-threshold', String(options.preferThreshold));
    if (options.aiThreshold) args.push('--ai-threshold', String(options.aiThreshold));
    if (options.action) args.push('--action', options.action);
    if (options.output) args.push('--output', options.output);
    const child = spawn('node', [scriptPath, ...args]);
    let output = '';
    child.stdout.on('data', (data) => (output += data.toString()));
    child.stderr.on('data', (data) => (output += data.toString()));
    child.on('close', () => resolve(output));
    child.on('error', (err) => reject(err));
  });
});
