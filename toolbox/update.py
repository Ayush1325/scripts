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
    containers: list[str] = get_all_containers()

    my_parser = argparse.ArgumentParser(
        description="Update Toolbox Containers", prog="toolbox-update"
    )
    my_parser.add_argument(
        "Containers", type=str, help="the names of the containers", nargs="*", choices=containers + ['all'], default='all'
    )

    args = my_parser.parse_args()

    containers_list = args.Containers

    if 'all' in containers_list:
        update_containers(containers)
    else:
        update_containers(containers_list)
