const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const fs = require('fs');

// Ensure logs folder exists
const logsDir = path.join(__dirname, 'logs');
if (!fs.existsSync(logsDir)) {
  fs.mkdirSync(logsDir);
  console.log("Logs folder created at:", logsDir);
} else {
  console.log("Logs folder exists at:", logsDir);
}

// Create the browser window
function createWindow() {
  const win = new BrowserWindow({
    width: 400,
    height: 700,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false
    }
  });

  win.loadFile('index.html');
}

// Markdown generator helper
function generateMarkdown(data) {
  return `# Receipt

**Mode:** ${data.mode === 'given' ? `From Q → To ${data.to}` : `From ${data.from} → To Q`}

**Date:** ${new Date().toLocaleString()}

**Items:**
${data.items.map(i => `- ${i.item} x${i.qty} @ ${i.price} = ${i.total}`).join('\n')}

**Grand Total:** $${data.grandTotal}

**Payment:** ${data.cash ? 'Cash ' : ''}${data.trade ? 'Trade ' : ''}${data.qbo ? 'QBO Logged' : ''}

**Notes:** ${data.notes}
`;
}

// IPC listener to save receipts
ipcMain.on('save-receipt', (event, data) => {
  const timestamp = Date.now();

  // Save JSON
  const jsonPath = path.join(logsDir, `receipt-${timestamp}.json`);
  fs.writeFileSync(jsonPath, JSON.stringify(data, null, 2));

  // Save Markdown
  const mdPath = path.join(logsDir, `receipt-${timestamp}.md`);
  fs.writeFileSync(mdPath, generateMarkdown(data));

  console.log(`Receipt saved: ${jsonPath}`);
});

// Electron app lifecycle
app.whenReady().then(() => {
  createWindow();

  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') app.quit();
});
