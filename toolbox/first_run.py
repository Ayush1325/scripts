#!/bin/python3

import subprocess
import argparse
import os


def pretty_block(func):
    def inner(*args, **kwargs):
        func(*args, **kwargs)
        print("")

    return inner


@pretty_block
def toolbox_run(container_name, commmand):
    cmd = ["toolbox", "run", "-c", container_name] + commmand
    subprocess.run(cmd)


@pretty_block
def update_container(container_name):
    print("System Upgrade")
    toolbox_run(container_name, ["sudo", "dnf", "upgrade", "-y"])


@pretty_block
def dnf_configuration(container_name):
    print("Dnf Configuration")
    toolbox_run(
        container_name,
        ["sudo", "sh", "-c", "echo", "deltarpm=true", ">>", "/etc/dnf/dnf.conf"],
    )
    toolbox_run(
        container_name,
        [
            "sudo",
            "sh",
            "-c",
            "echo",
            "max_parallel_downloads=12",
            ">>",
            "/etc/dnf/dnf.conf",
        ],
    )


@pretty_block
def install_basic_packages(container_name):
    print("Install Basic Packages")
    packages = ["fish", "exa", "direnv", "fd-find", "ripgrep"]
    toolbox_run(
        container_name,
        ["sudo", "dnf", "install", "-y"] + packages,
    )


@pretty_block
def install_development_packages(container_name):
    print("Install Development Packages")
    packages = ["neovim", "bat", "gcc", "g++"]
    toolbox_run(container_name, ["sudo", "dnf", "install", "-y"] + packages)


@pretty_block
def create_container(container_name):
    print("Create Container")
    subprocess.run(["toolbox", "create", container_name])


if __name__ == "__main__":
    my_parser = argparse.ArgumentParser(
        description="Create and Setup Toolbox Container", prog="toolbox-custom-create"
    )
    my_parser.add_argument(
        "Name", metavar="name", type=str, help="the name of the container"
    )
    my_parser.add_argument(
        "-d", "--development", action="store_true", help="install development tools"
    )
    args = my_parser.parse_args()

    container_name = args.Name

    create_container(container_name)
    dnf_configuration(container_name)
    update_container(container_name)
    install_basic_packages(container_name)
    if args.development:
        install_development_packages(container_name)
    os.environ["SHELL"] = "/bin/fish"
    subprocess.run(["toolbox", "enter", container_name])
