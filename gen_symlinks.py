import os

scripts = {
    "toolbox-custom-create": "../toolbox/first_run.py",
    "toolbox-update": "../toolbox/update.py",
    "toolbox-add-packages": "../toolbox/add_package.py"
}

if __name__ == "__main__":
    tmp = "./bin/tmp"
    for key, val in scripts.items():
        os.symlink(val, tmp)
        os.rename(tmp, "./bin/" + key)
