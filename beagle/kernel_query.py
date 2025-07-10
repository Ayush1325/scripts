#!/bin/python3
import subprocess
from argparse import ArgumentParser


BEAGLE_KERNEL_URL = "https://github.com/beagleboard/linux.git"


# Convert the major-minor-patch version format into an int for easier comparison
def version_to_int(major: int, minor: int, patch: int) -> int:
    return major * 10000 + minor * 100 + patch


def create_parser() -> ArgumentParser:
    parser = ArgumentParser(description="Show all beagle kernel branches")
    parser.add_argument(
        "--major", type=int, default=0, help="Minimum Kernel major version"
    )
    parser.add_argument(
        "--minor", type=int, default=0, help="Minimum Kernel minor version"
    )
    parser.add_argument(
        "--patch", type=int, default=0, help="Minimum Kernel patch version"
    )
    return parser


if __name__ == "__main__":
    args = create_parser().parse_args()
    current_version = version_to_int(args.major, args.minor, args.patch)

    branches = []
    resp = subprocess.run(
        ["git", "ls-remote", "-b", BEAGLE_KERNEL_URL],
        capture_output=True,
    )

    for line in resp.stdout.splitlines():
        branch = line.split()[1].split(b"/")[2]
        temp = branch.split(b".")
        # Ignore other branches
        if len(temp) == 3:
            major, minor, patch = temp
            major = int(major.lstrip(b"v"))
            minor = int(minor)
            patch = int(patch.split(b"-")[0])
            branches.append((branch.decode(), (major, minor, patch)))

    branches.sort(key=lambda x: version_to_int(x[1][0], x[1][1], x[1][2]))
    result = list(
        map(
            lambda x: x[0],
            filter(
                lambda x: version_to_int(x[1][0], x[1][1], x[1][2]) >= current_version,
                branches,
            ),
        )
    )

    for b in result:
        print(b)
