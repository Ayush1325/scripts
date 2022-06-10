#!/bin/python3
import argparse
import subprocess
import shutil
import sys
from os import path
from enum import Enum
from tempfile import TemporaryDirectory


class Architecture(Enum):
    IA32 = "qemu-system-i386"
    X64 = "qemu-system-x86_64"
    ARM = "qemu-system-arm"
    AARCH64 = "qemu-system-aarch64"
    RISCV64 = "qemu-system-riscv64"


def qemu_run(
    qemu_path: str,
    drive_dir: str,
    ovmf_code_path: str,
    ovmf_vars_path: str,
    extra_args: list[str],
):
    drive_command = lambda u, f: [
        "-drive",
        f"if=pflash,format=raw,unit={u},file={f},readonly=on",
    ]
    subprocess.run(
        [
            qemu_path,
            "-drive",
            f"file=fat:rw:{drive_dir},format=raw",
            "-net",
            "none",
        ]
        + drive_command(0, ovmf_code_path)
        + drive_command(1, ovmf_vars_path)
        + extra_args
    )


def setup_cli():
    my_parser = argparse.ArgumentParser(
        description="Run UEFI applications using qemu", prog="run-qemu"
    )
    my_parser.add_argument(
        "EFI_File",
        metavar="efi_file",
        type=str,
        help="path to efi file",
    )
    my_parser.add_argument(
        "-c",
        "--code",
        type=str,
        help="path to OVMF Code file",
        default="/usr/share/OVMF/OVMF_CODE.fd",
    )
    my_parser.add_argument(
        "-v",
        "--vars",
        type=str,
        help="path to OVMF Vars file",
        default="/usr/share/OVMF/OVMF_VARS.fd",
    )
    my_parser.add_argument(
        "-q",
        "--qemu",
        type=str,
        help=f"path to qemu executable. [Default Value: {Architecture.X64.value}]",
    )
    my_parser.add_argument(
        "-a",
        "--arch",
        choices=Architecture,
        type=Architecture.__getitem__,
        help="arhitecture to emulate on, [Default Value: X64]",
        default=Architecture.X64.name,
    )

    return my_parser


def setup_mount_dir(tempdir, efi_file):
    shutil.copyfile(efi_file, path.join(tempdir, "run.efi"))

    with open(path.join(tempdir, "startup.nsh"), "w") as startup_file:
        lines = ["@echo -off", "fs0:", "echo Starting UEFI Application...", "run.efi"]
        startup_file.write("\n".join(lines))


def parse_args() -> tuple[list[str], list[str]]:
    try:
        break_point = sys.argv.index("--")
        return sys.argv[1:break_point], sys.argv[break_point + 1 :]
    except ValueError:
        return sys.argv[1:], []


if __name__ == "__main__":
    args, extra_args = parse_args()
    args = setup_cli().parse_args(args)

    qemu_path = args.qemu
    ovmf_vars_path = args.vars
    ovmf_code_path = args.code

    with TemporaryDirectory() as tempdir:
        setup_mount_dir(tempdir, args.EFI_File)

        if qemu_path:
            qemu_run(qemu_path, tempdir, ovmf_code_path, ovmf_vars_path, extra_args)
        else:
            arch = args.arch
            qemu_run(arch.value, tempdir, ovmf_code_path, ovmf_vars_path, extra_args)
