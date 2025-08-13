import sys
import os
import subprocess

from constants.path import TESSERACT_EXE

sys.path.append(os.path.dirname(__file__))
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "application", "src"))
)
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "application", "lib"))
)


def install(package):
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            package,
            "--proxy=http://11.56.30.169:3142",
            "--trusted-host",
            "pypi.org",
            "--trusted-host",
            "files.pythonhost",
            "--trusted-host",
            "proxy_amer.safran:9009"
        ]
    )


def get_libraries():
    with open("requirements.txt", encoding="utf-8") as f:
        required_libraries = [
            line.strip() for line in f if line.strip() and not line.startswith("#")
        ]

    for lib in required_libraries:
        try:
            __import__(lib.split(",")[1])
            print(f"{lib.split(",")[0]} is already installed.")
        except ImportError:
            print(f"Installing {lib.split(",")[0]}...")
            install(lib.split(",")[0])


def launch():
    from application import App

    app = App()
    app.run()


if __name__ == "__main__":
    print(
        "\n\n\nRunning Auto Filter\n\n-----------------------------\n\nCreated by Nicolas Fagot\n\n"
    )
    print("Installing libraries ...")
    get_libraries()
    os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
    print("\n\n\nLibraries installed\n\n")
    while not os.path.exists(TESSERACT_EXE):
        print("Please install tesseract using admin permission before continuing.\nA shortcut to the Tesseract exe has been created on your desktop.")
        input("\nPress Enter when tesseract is installed to continue\n")
    print("\n\nLaunching the program, next time you can use the shortcut on your desktop.\n\n")
    launch()
