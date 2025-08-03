const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  runDuplicateCleaner: (options) =>
    ipcRenderer.invoke('run-duplicate-cleaner', options),
});
