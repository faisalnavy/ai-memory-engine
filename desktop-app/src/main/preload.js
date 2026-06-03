const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  selectFolder:  ()      => ipcRenderer.invoke('select-folder'),
  openExternal:  (url)   => ipcRenderer.invoke('open-external', url),
  getApiPort:    ()      => ipcRenderer.invoke('get-api-port'),
});
