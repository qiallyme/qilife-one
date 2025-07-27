const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  runFileFlow: () => ipcRenderer.invoke('run-file-flow'),
  getSettings: () => ipcRenderer.invoke('get-settings'),
  saveSettings: (data) => ipcRenderer.send('save-settings', data)
});
