import os

scripts = {
        "toolbox-update": "../toolbox/update.sh"
}

if __name__ == "__main__":
    for key,val in scripts.items():
        os.symlink(val, "./bin/" + key)
