const { app, BrowserWindow, Menu, globalShortcut } = require("electron");

const path = require("path");
const waitOn = require("wait-on");

import { startBackend, stopBackend } from "./backend.js";

function prepareWindow() {
  if (process.platform === "win32") {
    app.setAppUserModelId(app.name);
  }

  if (app.isPackaged) {
    const iconPath = path.join(process.resourcesPath, "frontend", "icon.png");
    app.dock.setIcon(iconPath);
  }
  
  Menu.setApplicationMenu(null);

  // Bloquer les raccourcis clavier courants des DevTools (F12, Ctrl+Shift+I, Cmd+Orf+I)
  globalShortcut.register("CommandOrControl+Shift+I", () => {
    return false; // Ne fait rien
  });
  globalShortcut.register("F12", () => {
    return false;
  });
}

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
  // win.webContents.on("devtools-opened", () => {
  //   win.webContents.closeDevTools();
  // });
}

app.whenReady().then(async () => {
  // prepareWindow();

  startBackend(app);

  await createWindow();
});

app.on("window-all-closed", () => {
  stopBackend();

  if (process.platform !== "darwin") {
    app.quit();
  }
});

app.on("will-quit", () => {
  globalShortcut.unregisterAll();
});
