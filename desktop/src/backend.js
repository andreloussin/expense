import { spawn } from "node:child_process";
import path from "node:path";


let backendProcess = null;


export function startBackend(app){


    let backendPath;


    if(app.isPackaged){

        backendPath = path.join(
            process.resourcesPath,
            "backend",
            "expense-server.exe"
        );


    }else{


        backendPath = path.join(
            process.cwd(),
            "resources",
            "backend",
            "expense-server.exe"
        );

    }



    console.log(
        "Starting backend:",
        backendPath
    );



    backendProcess = spawn(
        backendPath,
        [],
        {
            windowsHide:true,
            detached:false
        }
    );



    backendProcess.stdout.on(
        "data",
        data=>{

            console.log(
                "[DJANGO]",
                data.toString()
            );

        }
    );



    backendProcess.stderr.on(
        "data",
        data=>{

            console.error(
                "[DJANGO ERROR]",
                data.toString()
            );

        }
    );



    backendProcess.on(
        "exit",
        code=>{

            console.log(
                "Backend stopped:",
                code
            );

        }
    );



    backendProcess.on(
        "error",
        err=>{

            console.error(
                "Backend launch failed",
                err
            );

        }
    );

}



export function stopBackend(){


    if(
        backendProcess
    ){

        console.log(
            "Stopping backend..."
        );


        backendProcess.kill();

        backendProcess=null;

    }

}