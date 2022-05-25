import os

scripts = {
    "toolbox-update": "../toolbox/update.sh",
    # "toolbox-first-run": "../toolbox/first-run.sh",
    "toolbox-custom-create": "../toolbox/first_run.py",
}

if __name__ == "__main__":
    tmp = "./bin/tmp"
    for key, val in scripts.items():
        os.symlink(val, tmp)
        os.rename(tmp, "./bin/" + key)
