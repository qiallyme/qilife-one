const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

// Python backend configuration
const PYTHON_API_URL = 'http://127.0.0.1:8000';
const PYTHON_BACKEND_PATH = path.join(__dirname, '..', '..', 'python-backend');

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
    },
  });
  
  // Load the built React app from the dist directory
  const distPath = path.join(__dirname, '..', '..', 'dist', 'index.html');
  
  if (require('fs').existsSync(distPath)) {
    console.log('📦 Loading built app from:', distPath);
    win.loadFile(distPath);
  } else {
    console.log('⚠️ Built app not found, loading development version');
    // Fallback to development server
    win.loadURL('http://localhost:5173');
  }
}

app.whenReady().then(createWindow);
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

// Start Python backend server
function startPythonBackend() {
  console.log('🐍 Starting Python backend server...');
  
  const pythonProcess = spawn('python', ['-m', 'uvicorn', 'main:app', '--host', '127.0.0.1', '--port', '8000'], {
    cwd: PYTHON_BACKEND_PATH,
    stdio: 'pipe'
  });
  
  pythonProcess.stdout.on('data', (data) => {
    console.log('🐍 Python backend:', data.toString());
  });
  
  pythonProcess.stderr.on('data', (data) => {
    console.error('🐍 Python backend error:', data.toString());
  });
  
  pythonProcess.on('close', (code) => {
    console.log(`🐍 Python backend exited with code ${code}`);
  });
  
  return pythonProcess;
}

// IPC handler for API calls to Python backend
ipcMain.handle('call-python-api', async (_event, endpoint, data) => {
  try {
    const response = await fetch(`${PYTHON_API_URL}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('API call error:', error);
    throw error;
  }
});

// IPC handler for duplicate cleaner (now via API)
ipcMain.handle('run-duplicate-cleaner', async (_event, options) => {
  try {
    const response = await fetch(`${PYTHON_API_URL}/fileflow/duplicate-cleaner`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(options),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Duplicate cleaner API error:', error);
    throw error;
  }
});

// Start Python backend when app starts
app.whenReady().then(() => {
  createWindow();
  startPythonBackend();
});
