const {
  app,
  BrowserWindow,
  Menu
} = require("electron");


const path = require("path");
const { spawn } = require("child_process");
const waitOn = require("wait-on");


let backendProcess;


function startBackend() {

    let backendPath;


    if (app.isPackaged) {

        backendPath = path.join(
            process.resourcesPath,
            "backend",
            "expense-server.exe"
        );

    } else {

        backendPath = path.join(
            __dirname,
            "..",
            "..",
            "resources",
            "backend",
            "expense-server.exe"
        );
    }


    backendProcess = spawn(
        backendPath,
        [],
        {
            windowsHide: true
        }
    );

    backendProcess.on('error', (err) => {
      console.error("BACKEND ERROR:", err);
    });


    backendProcess.stdout.on(
        "data",
        data => {
            console.log(
                data.toString()
            );
        }
    );


    backendProcess.stderr.on(
        "data",
        data => {
            console.error(
                data.toString()
            );
        }
    );
}



async function createWindow() {


    await waitOn({
        resources:[
            "http://127.0.0.1:8765/api/categories/"
        ],
        timeout:30000
    });



    const win = new BrowserWindow({

        width:1200,
        height:800,

        webPreferences:{
            preload:path.join(
                __dirname,
                "preload.js"
            )
        }

    });


    if(app.isPackaged){

        win.loadFile(
            path.join(
                process.resourcesPath,
                "frontend",
                "index.html"
            )
        );

    }else{

        win.loadFile(
            path.join(
                __dirname,
                "..",
                "..",
                "resources",
                "frontend",
                "index.html"
            )
        );
    }

}



app.whenReady()
.then(async()=>{

    Menu.setApplicationMenu(null);

    startBackend();

    await createWindow();

});



app.on(
    "window-all-closed",
    ()=>{

        if(backendProcess){
            backendProcess.kill();
        }


        if(process.platform!=="darwin"){
            app.quit();
        }

    }
);