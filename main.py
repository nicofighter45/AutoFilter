import sys
import os
import subprocess

sys.path.append(os.path.dirname(__file__))
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "application", "src"))
)


def install(package):
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            package,
            "--proxy",
            "proxy_amer.safran:9009",
        ]
    )


def get_libraries():
    with open("requirements.txt", encoding="utf-8") as f:
        required_libraries = [
            line.strip() for line in f if line.strip() and not line.startswith("#")
        ]

    for lib in required_libraries:
        try:
            __import__(lib)
        except ImportError:
            print(f"Installing {lib}...")
            install(lib)
        else:
            print(f"{lib} is already installed.")


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
    print("\n\n\nLibraries installed, launching\n\n")
    launch()
