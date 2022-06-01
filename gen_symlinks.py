import os

scripts = {
    "toolbox-custom-create": "../toolbox/first_run.py",
    "toolbox-update": "../toolbox/update.py",
}

if __name__ == "__main__":
    tmp = "./bin/tmp"
    for key, val in scripts.items():
        os.symlink(val, tmp)
        os.rename(tmp, "./bin/" + key)
