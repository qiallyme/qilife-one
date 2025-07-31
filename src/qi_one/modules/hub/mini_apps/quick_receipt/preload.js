import { contextBridge, ipcRenderer } from 'electron';

contextBridge.exposeInMainWorld('electronAPI', {
  saveReceipt: (data) => ipcRenderer.send('save-receipt', data)
});
