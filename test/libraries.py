import subprocess
import sys

# List your required libraries here
required_libraries = [
    "easyOCR",
    "keyboard",
    "PyPDF2"
]

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--proxy", "proxy_amer.safran:9009"])

if __name__ == "__main__":
    for lib in required_libraries:
        try:
            __import__(lib)
        except ImportError:
            print(f"Installing {lib}...")
            install(lib)
        else:
            print(f"{lib} is already installed.")
