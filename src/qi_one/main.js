const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const fs = require('fs');
const { spawn, spawnSync } = require('child_process');

// --------- Paths ---------
const vaultLogPath = "Q:\\GoogleDriveStream\\qilife-vault\\o00inb_inbox_\\o00inbraw_raw-dumps_";
const venvDir = path.join(__dirname, '..', '..', '.venv');
const pythonPath = path.join(venvDir, 'Scripts', 'python.exe');
const requirementsPath = path.join(__dirname, '..', '..', 'requirements.txt');
const settingsFile = path.join(app.getPath('userData'), 'settings.json');

// --------- Ensure venv & deps ---------
function ensureVenvAndDeps() {
  if (!fs.existsSync(venvDir)) {
    console.log("Creating virtual environment...");
    spawnSync('python', ['-m', 'venv', venvDir], { stdio: 'inherit' });
  }

  console.log("Upgrading pip...");
  spawnSync(pythonPath, ['-m', 'pip', 'install', '--upgrade', 'pip'], { stdio: 'inherit' });

  console.log("Installing requirements...");
  spawnSync(pythonPath, ['-m', 'pip', 'install', '-r', requirementsPath], { stdio: 'inherit' });
}

// --------- Create Electron Window ---------
function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true
    },
    icon: path.join(__dirname, 'qlife.png')
  });

  win.loadFile('index.html');
}

// --------- Vault Logging ---------
function logToVault(filename, content) {
  try {
    if (!fs.existsSync(vaultLogPath)) {
      fs.mkdirSync(vaultLogPath, { recursive: true });
    }
    const logFile = path.join(vaultLogPath, filename);
    fs.writeFileSync(logFile, content);
    console.log(`Logged to vault: ${logFile}`);
  } catch (err) {
    console.error("Vault logging failed:", err);
  }
}

// --------- IPC: Save Receipt ---------
ipcMain.on('save-receipt', (event, data) => {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const jsonLog = `receipt-${timestamp}.json`;
  const mdLog = `receipt-${timestamp}.md`;

  // JSON log
  logToVault(jsonLog, JSON.stringify(data, null, 2));

  // Markdown log
  const mdContent = `# Receipt - ${timestamp}\n\n${data.items
    .map(i => `- ${i.quantity} x ${i.name} @ $${i.price.toFixed(2)}`)
    .join('\n')}\n\n**Total:** $${data.total.toFixed(2)}\n\nNotes: ${data.notes || ''}`;
  logToVault(mdLog, mdContent);
});

// --------- IPC: Run FileFlow ---------
ipcMain.handle('run-file-flow', async () => {
  try {
    const corePath = path.join(__dirname, 'modules', 'fileflow', 'core.py');
    const processOutput = spawnSync(pythonPath, [corePath], { encoding: 'utf-8' });

    if (processOutput.error) throw processOutput.error;
    return processOutput.stdout || processOutput.stderr;
  } catch (err) {
    return `Error running FileFlow: ${err.message}`;
  }
});

// --------- IPC: Save Settings ---------
ipcMain.handle('save-settings', async (event, settings) => {
  try {
    fs.writeFileSync(settingsFile, JSON.stringify(settings, null, 2));
    logToVault('settings-log.md', `## Settings Updated\n\`\`\`json\n${JSON.stringify(settings, null, 2)}\n\`\`\``);
    return true;
  } catch (err) {
    console.error("Failed to save settings:", err);
    return false;
  }
});

// --------- App Lifecycle ---------
app.whenReady().then(() => {
  ensureVenvAndDeps();
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});