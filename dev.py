import os
import sys
import subprocess
from pathlib import Path


ROOT = Path(__file__).parent.resolve()
processes = []

def run_process(command, cwd):
    print(f"Starting: {' '.join(command)}")
    process = subprocess.Popen(
        command,
        cwd=cwd,
        shell=True
    )
    
    processes.append(process)

    return process

def stop_all():

    print("\nStopping services...")

    for process in processes:
        try:
            if os.name == "nt":
                # Windows
                subprocess.run(
                    [
                        "taskkill",
                        "/F",
                        "/T",
                        "/PID",
                        str(process.pid)
                    ],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )

            else:
                # Linux / macOS
                os.killpg(
                    os.getpgid(process.pid),
                    signal.SIGTERM
                )

        except Exception as e:
            print(f"Stop error: {e}")

    print("All services stopped.")

def backend():
    print("Starting Django backend...")
    python = ROOT / "backend" / ".venv" / "Scripts" / "python.exe"

    if not python.exists():
        python = "python"

    run_process(
        [
            str(python),
            "manage.py",
            "runserver"
        ],
        ROOT / "backend"
    )


def frontend():
    print("Starting Vue frontend...")
    run_process(
        [
            "npm",
            "run",
            "dev"
        ],
        ROOT / "frontend"
    )


def desktop():
    print("Starting Electron...")
    run_process(
        [
            "npm",
            "start"
        ],
        ROOT / "desktop"
    )


def electron_build():
    print("Building Vue...")
    subprocess.run(
        [
            "npm",
            "run",
            "build"
        ],
        cwd=ROOT / "frontend",
        shell=True
    )

    print("Building Electron...")
    subprocess.run(
        [
            "npm",
            "run",
            "make"
        ],
        cwd=ROOT / "desktop",
        shell=True
    )


def all_services():
    backend()
    frontend()
    try:
        while True:
            # garde le script vivant
            for p in processes:
                if p.poll() is not None:
                    print("A service stopped unexpectedly")

            import time
            time.sleep(1)

    except KeyboardInterrupt:
        stop_all()


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print(
            """
            Usage:

            python dev.py backend
            python dev.py frontend
            python dev.py desktop
            python dev.py all
            python dev.py electron-build
            """
        )

        sys.exit(1)

    command = sys.argv[1]

    commands = {
        "backend": backend,
        "frontend": frontend,
        "desktop": desktop,
        "all": all_services,
        "electron-build": electron_build
    }

    if command not in commands:
        print("Unknown command")
        sys.exit(1)

    try:
        commands[command]()
    except KeyboardInterrupt:
        stop_all()