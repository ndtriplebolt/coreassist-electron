const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // Get backend configuration
  getBackendConfig: () => ipcRenderer.invoke('get-backend-config'),
  
  // Get app version
  getVersion: () => ipcRenderer.invoke('app-version'),
  
  // Platform info
  platform: process.platform,
  
  // Future API methods for voice commands, auth, etc.
  auth: {
    // These will be implemented as you build the app
    signIn: (credentials) => ipcRenderer.invoke('auth-sign-in', credentials),
    signOut: () => ipcRenderer.invoke('auth-sign-out'),
    getToken: () => ipcRenderer.invoke('auth-get-token')
  },
  
  voice: {
    // Voice command APIs will go here
    startListening: () => ipcRenderer.invoke('voice-start-listening'),
    stopListening: () => ipcRenderer.invoke('voice-stop-listening')
  },
  
  services: {
    // Service integration APIs
    connectService: (service) => ipcRenderer.invoke('services-connect', service),
    disconnectService: (service) => ipcRenderer.invoke('services-disconnect', service),
    getConnectedServices: () => ipcRenderer.invoke('services-list')
  }
});