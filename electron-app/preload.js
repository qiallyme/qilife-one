const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  callPythonAPI: (endpoint, data) => ipcRenderer.invoke('call-python-api', endpoint, data),
  runDuplicateCleaner: (options) => ipcRenderer.invoke('run-duplicate-cleaner', options),
});
