// See the Electron documentation for details on how to use preload scripts:
// https://www.electronjs.org/docs/latest/tutorial/process-model#preload-scripts

const { contextBridge } = require("electron");

const arg = process.argv.find((x) => x.startsWith("--api-url="));

const apiUrl = arg?.replace("--api-url=", "");

contextBridge.exposeInMainWorld("config", {
  API_URL: apiUrl,
});
