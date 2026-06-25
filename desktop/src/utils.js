import net from "net";
import { Menu, globalShortcut } from "electron";
import { stopBackend } from "./backend.js";

function getFreePort() {
  return new Promise((resolve, reject) => {
    const server = net.createServer();

    server.listen(0, "127.0.0.1", () => {
      const port = server.address().port;

      server.close(() => {
        resolve(port);
      });
    });

    server.on("error", reject);
  });
}

function prepareWindow(app) {
  if (process.platform === "win32") {
    app.setAppUserModelId(app.name);
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

const quitWindow = () => {
  globalShortcut.unregisterAll();
  stopBackend();
};

export { getFreePort, prepareWindow, quitWindow };
