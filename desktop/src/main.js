const { app, BrowserWindow, Menu } = require("electron");

const path = require("path");
const waitOn = require("wait-on");

import { startBackend, stopBackend } from "./backend.js";

let backendProcess;

async function createWindow() {
  await waitOn({
    resources: ["tcp:8765"],
    timeout: 3000,
  });

  const win = new BrowserWindow({
    width: 1200,
    height: 800,

    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
    },
  });

  if (app.isPackaged) {
    win.loadFile(path.join(process.resourcesPath, "frontend", "index.html"));
  } else {
    win.loadFile(
      path.join(__dirname, "..", "..", "resources", "frontend", "index.html")
    );
  }

  // Bloquer l'ouverture des DevTools via le code
  win.webContents.on("devtools-opened", () => {
    win.webContents.closeDevTools();
  });
}

app.whenReady().then(async () => {
  Menu.setApplicationMenu(null);

  startBackend(app);

  await createWindow();
});

app.on("window-all-closed", () => {
  stopBackend();

  if (process.platform !== "darwin") {
    app.quit();
  }
});
