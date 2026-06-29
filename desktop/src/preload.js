// See the Electron documentation for details on how to use preload scripts:
// https://www.electronjs.org/docs/latest/tutorial/process-model#preload-scripts

const { contextBridge, ipcRenderer } = require("electron");

// 1. Récupération de l'argument d'API Port injecté par le processus principal
const arg = process.argv.find((x) => x.startsWith("--api-url="));
const apiUrl = arg ? arg.replace("--api-url=", "") : null;

// Exposition de la configuration globale pour le Frontend Vue.js local
contextBridge.exposeInMainWorld("config", {
  API_URL: apiUrl,
});

// 2. Passerelle de communication pour le système de licences
contextBridge.exposeInMainWorld("electronAPI", {
  getMachineId: () => {
    return ipcRenderer.sendSync("get-machine-id-sync");
  },

  saveLicense: (license) => {
    ipcRenderer.send("save-license-cmd", license);
  },

  getLicense: () => {
    return ipcRenderer.sendSync("get-license-sync");
  },

  clearLicense: () => {
    ipcRenderer.send("clear-license-cmd");
  },

  checkLicense: () => {
    return ipcRenderer.invoke("check-license");
  },
});
