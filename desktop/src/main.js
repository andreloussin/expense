import { app, BrowserWindow, ipcMain } from "electron";
import path from "node:path";
import Store from "electron-store";

import { startBackend, stopBackend } from "./backend.js";
import { prepareWindow, getFreePort, quitWindow } from "./utils.js";
import {
  verifyLicenseOffline,
  getMachineId,
  clearLicense,
  getLicense,
  saveLicense,
} from "./licence.js";

import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const store = new Store({ name: "license" });

let mainWindow = null;
let backendPort = null;

/**
 * Gestionnaire IPC pour la page d'activation HTML
 */
ipcMain.handle("check-license", async () => {
  const result = verifyLicenseOffline();

  // Si l'utilisateur vient de valider une clé correcte, on bascule vers l'application principale
  if (result.valid && mainWindow) {
    loadMainFrontend(mainWindow, backendPort);
  }

  return result;
});

// --- INTERCEPTION DES ÉVÉNEMENTS DU PRELOAD ---

// Renvoie de manière synchrone l'UUID matériel au Preload
ipcMain.on("get-machine-id-sync", (event) => {
  event.returnValue = getMachineId();
});

// Récupère la licence stockée sur le disque dur
ipcMain.on("get-license-sync", (event) => {
  event.returnValue = getLicense();
});

// Sauvegarde la licence reçue dans le store local
ipcMain.on("save-license-cmd", (event, license) => {
  clearLicense();
  saveLicense(license);
});

// Supprime définitivement la licence (en cas d'erreur ou d'expiration)
ipcMain.on("clear-license-cmd", () => {
  clearLicense();
});

/**
 * Charge l'application finale une fois activée
 */
function loadMainFrontend(win, port) {
  if (app.isPackaged) {
    win.loadFile(path.join(process.resourcesPath, "frontend", "index.html"));
  } else {
    win.loadFile(
      path.join(__dirname, "..", "resources", "frontend", "index.html")
    );
  }
}

async function createWindow(port) {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      worldSafeExecuteJavaScript: true,
      nodeIntegration: false,
      additionalArguments: [`--api-url=http://127.0.0.1:${port}/api`],
    },
  });

  // --- LE COEUR DE LA LOGIQUE D'AIGUILLAGE ---
  const licenseCheck = verifyLicenseOffline();

  if (licenseCheck.valid) {
    await startBackend(app, backendPort)
      .then(() => {
        console.log(`Backend started on port ${backendPort}`);
      })
      .catch((err) => {
        console.error("Failed to start backend:", err);
      });
    // La licence est OK, on lance l'application normalement
    loadMainFrontend(mainWindow, port);
  } else {
    // Pas de licence, on charge la page d'activation
    mainWindow.loadFile(path.join(__dirname, "activation.html"));
  }

  // Sécurité DevTools
  mainWindow.webContents.on("devtools-opened", () => {
    mainWindow.webContents.closeDevTools();
  });
}

app.whenReady().then(async () => {
  prepareWindow(app);

  backendPort = await getFreePort();

  await createWindow(backendPort);
});

app.on("window-all-closed", () => {
  stopBackend();
  if (process.platform !== "darwin") {
    app.quit();
  }
});

app.on("will-quit", quitWindow);
