import os

scripts = {
    "toolbox-custom-create": "./toolbox/first_run.py",
    "toolbox-update": "./toolbox/update.py",
    "toolbox-add-packages": "./toolbox/add_package.py",
    "run-qemu": "./Tianocore/RunQemu.py"
}

if __name__ == "__main__":
    tmp = "/home/ayush/.local/bin/tmp"
    for key, val in scripts.items():
        os.symlink(os.path.abspath(val), tmp)
        os.rename(tmp, "/home/ayush/.local/bin/" + key)
