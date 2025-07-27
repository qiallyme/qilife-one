const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  saveReceipt: (data) => ipcRenderer.send('save-receipt', data)
});
