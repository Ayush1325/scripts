#!/bin/python3
import subprocess
from argparse import ArgumentParser


BEAGLE_UBOOT_URL = "https://github.com/beagleboard/u-boot.git"


# Convert the year-month version format into an int for easier comparison
def version_to_int(year: int, month: int) -> int:
    return year * 100 + month


def create_parser() -> ArgumentParser:
    parser = ArgumentParser(description="Show all beagle U-Boot branches")
    parser.add_argument("--year", type=int, default=0, help="Minimum U-Boot year")
    parser.add_argument("--month", type=int, default=0, help="Minimum U-Boot month")
    parser.add_argument("board", type=str, help="Board Name")
    return parser


if __name__ == "__main__":
    args = create_parser().parse_args()
    current_version = version_to_int(args.year, args.month)

    branches = []
    resp = subprocess.run(
        ["git", "ls-remote", "-b", BEAGLE_UBOOT_URL, f"*-{args.board}"],
        capture_output=True,
    )

    for line in resp.stdout.splitlines():
        branch = line.split()[1].split(b"/")[2]
        temp = branch.split(b".")
        # Ignore other branches
        if len(temp) == 2:
            year, month = temp
            year = int(year.lstrip(b"v"))
            month = int(month.split(b"-")[0])
            branches.append((branch.decode(), (year, month)))

    branches.sort(key=lambda x: version_to_int(x[1][0], x[1][1]))
    result = list(
        map(
            lambda x: x[0],
            filter(
                lambda x: version_to_int(x[1][0], x[1][1]) >= current_version,
                branches,
            ),
        )
    )

    for b in result:
        print(b)
