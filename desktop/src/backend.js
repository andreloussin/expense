import { spawn } from "node:child_process";
import path from "node:path";
import http from "node:http";

let backendProcess = null;

function startBackend(app, port = 8765) {
  return new Promise((resolve, reject) => {
    let backendPath;

    if (app.isPackaged) {
      backendPath = path.join(
        process.resourcesPath,
        "backend",
        "expense-server.exe"
      );
    } else {
      backendPath = path.join(
        process.cwd(),
        "resources",
        "backend",
        "expense-server.exe"
      );
    }

    console.log("Starting backend:", backendPath);

    const backendProcess = spawn(backendPath, ["--port", String(port)], {
      windowsHide: true,
      detached: false,
    });

    backendProcess.stdout.on("data", (data) => {
      console.log("[DJANGO]", data.toString());
    });

    backendProcess.stderr.on("data", (data) => {
      console.error("[DJANGO ERROR]", data.toString());
    });

    backendProcess.on("exit", (code) => {
      console.log("Backend stopped:", code);
    });

    backendProcess.on("error", (err) => {
      console.error("Backend launch failed", err);
      reject(err);
    });

    backendProcess.stderr.on("data", (data) => {
      const msg = data.toString();

      console.error("[DJANGO ERROR]", msg);

      if (msg.includes("Serving on")) {
        resolve(backendProcess);
      }
    });
  });
}

function stopBackend() {
  if (backendProcess) {
    console.log("Stopping backend...");

    backendProcess.kill();

    backendProcess = null;
  }
}
function waitForBackend(port, timeout = 30000) {
  const start = Date.now();
  return new Promise((resolve, reject) => {
    function check() {
      const req = http.get(`http://127.0.0.1:${port}/health/`, (response) => {
        if (response.statusCode === 200) {
          resolve();
        } else {
          retry();
        }
      });

      req.on("error", retry);
      req.end();
    }

    function retry() {
      if (Date.now() - start > timeout) {
        reject(new Error("Backend timeout"));
        return;
      }
      setTimeout(check, 500);
    }

    check();
  });
}

export {
  startBackend,
  stopBackend,
  waitForBackend,
};
