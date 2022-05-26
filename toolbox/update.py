#!/bin/python3
import argparse
import subprocess


def pretty_block(func):
    def inner(*args, **kwargs):
        func(*args, **kwargs)
        print("")

    return inner


@pretty_block
def update_container(container_name: str):
    print("Updating " + container_name)
    subprocess.run(
        ["toolbox", "run", "-c", container_name, "sudo", "dnf", "upgrade", "-y"]
    ).check_returncode()


def update_containers(containers: list[str]):
    for container in containers:
        update_container(container)


def get_all_containers() -> list[str]:
    process = subprocess.run(["toolbox", "list", "-c"], stdout=subprocess.PIPE)
    containers = list(
        map(lambda x: x.split()[1].decode("utf-8"), process.stdout.splitlines()[1:])
    )
    return containers


if __name__ == "__main__":
    my_parser = argparse.ArgumentParser(
        description="Update Toolbox Containers", prog="toolbox-update"
    )
    my_parser.add_argument(
        "-c", "--containers", type=str, help="the names of the containers", nargs="+"
    )
    my_parser.add_argument(
        "-a", "--all", action="store_true", help="update all containers"
    )

    args = my_parser.parse_args()

    if args.all:
        containers = get_all_containers()
        update_containers(containers)
    elif args.containers:
        update_containers(args.containers)
