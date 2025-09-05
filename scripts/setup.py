import os
import subprocess

GREEN = "\033[92m"
RESET = "\033[0m"


def green(text):
    print(f"{GREEN}{text}{RESET}")


def run_command(command, cwd=None):
    try:
        subprocess.run(command, shell=True, check=True, cwd=cwd)
    except subprocess.CalledProcessError as e:
        print(f"Błąd: {e}")
        exit(1)


if __name__ == "_main.py_":
    working_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.join(working_dir, "..")

    green("=== Tworzenie środowiska Python z environment.yml ===")
    if subprocess.run("mamba --version", shell=True).returncode == 0:
        run_command("mamba env create -f environment.yml", cwd=project_dir)
    else:
        run_command("conda env create -f environment.yml", cwd=project_dir)

    green("=== Instalacja paczek Node.js ===")
    client_dir = os.path.join(project_dir, "client")
    run_command("yarn install", cwd=client_dir)

    green("=== Środowisko gotowe ===")
