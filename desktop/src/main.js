import { app, BrowserWindow } from "electron";
import path from "node:path";
import waitOn from "wait-on";

import { startBackend, stopBackend } from "./backend.js";
import { prepareWindow, getFreePort, quitWindow } from "./utils.js";

import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function createWindow(port) {
  await waitOn({
    resources: [`tcp:${port}`],
    timeout: 3000,
  });

  const win = new BrowserWindow({
    width: 1200,
    height: 800,

    webPreferences: {
      preload: path.join(__dirname, "preload.js"),

      additionalArguments: [
          `--api-url=http://127.0.0.1:${port}/api`
      ]
    },
  });

  if (app.isPackaged) {
    win.loadFile(path.join(process.resourcesPath, "frontend", "index.html"));
  } else {
    win.loadFile(
      path.join(__dirname, "..", "resources", "frontend", "index.html")
    );
  }

  // Bloquer l'ouverture des DevTools via le code
  win.webContents.on("devtools-opened", () => {
    win.webContents.closeDevTools();
  });
}

app.whenReady().then(async () => {
  prepareWindow(app);

  const port = await getFreePort();

  await startBackend(app, port)
    .then(() => {
      console.log(`Backend started on port ${port}`);
    })
    .catch((err) => {
      console.error("Failed to start backend:", err);
    });

  await createWindow(port);
});

app.on("window-all-closed", () => {
  stopBackend();

  if (process.platform !== "darwin") {
    app.quit();
  }
});

app.on("will-quit", quitWindow);
