#!/bin/python3
import argparse
import subprocess


def pretty_block(func):
    def inner(*args, **kwargs):
        func(*args, **kwargs)
        print()

    return inner


def get_all_containers() -> list[str]:
    process = subprocess.run(["toolbox", "list", "-c"], stdout=subprocess.PIPE)
    containers = list(
        map(lambda x: x.split()[1].decode("utf-8"), process.stdout.splitlines()[1:])
    )
    return containers


@pretty_block
def add_package_to_container(container_name: str, packages: list[str]):
    print("Adding Packages to " + container_name)
    subprocess.run(
        ["toolbox", "run", "-c", container_name, "sudo", "dnf", "install", "-y"]
        + packages
    ).check_returncode()


def add_package_to_containers(containers: list[str], packages: list[str]):
    for container in containers:
        add_package_to_container(container, packages)


if __name__ == "__main__":
    my_parser = argparse.ArgumentParser(
        description="Add packages Toolbox Containers", prog="toolbox-add-packages"
    )
    my_parser.add_argument(
        "-c", "--containers", type=str, help="the names of the containers", nargs="+"
    )
    my_parser.add_argument(
        "-a", "--all", action="store_true", help="update all containers"
    )
    my_parser.add_argument(
        "Packages",
        metavar="packages",
        type=str,
        help="the names of the packages",
        nargs="+",
    )

    args = my_parser.parse_args()
    packages = args.Packages

    if args.all:
        containers = get_all_containers()
        add_package_to_containers(containers, packages)
    elif args.containers:
        add_package_to_containers(args.containers, packages)
