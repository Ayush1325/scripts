import os

scripts = {
    "toolbox-custom-create": "./toolbox/first_run.py",
    "toolbox-update": "./toolbox/update.py",
    "toolbox-add-packages": "./toolbox/add_package.py",
    "run-qemu": "./Tianocore/RunQemu.py"
}

local_bin_path = "/home/ayush/.local/bin"


def setup_dir():
    if not os.path.isdir(local_bin_path):
        os.mkdir(local_bin_path)
    

if __name__ == "__main__":
    setup_dir()
    tmp = os.path.join(local_bin_path, "tmp")
    for key, val in scripts.items():
        os.symlink(os.path.abspath(val), tmp)
        os.rename(tmp, os.path.join(local_bin_path, key))
