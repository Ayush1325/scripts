#!/bin/python3
import argparse
import subprocess
import shutil
import sys
import logging
from os import path
from tempfile import TemporaryDirectory
from dataclasses import dataclass


@dataclass
class QemuItem:
    qemu: str
    ovmf_code: str
    ovmf_vars: str
    uefi_shell: str


EFI_FILE_NAME: str = "run.efi"
STARTUP_FILE_NAME: str = "startup.nsh"
ROOTFS_IMG_NAME: str = "rootfs.img"
QEMU_BINARY_NAME: str = "qemu-system-x86_64"
OVMF_CODE_FILE_NAME: str = "OVMF_CODE.fd"
OVMF_VARS_FILE_NAME: str = "OVMF_VARS.fd"
UEFI_SHELL_FILE_NAME: str = "UefiShell.iso"
DEFAULT_ARCH: str = "X86_64"
DEFAULT_STARTUP_SCRIPT = ["@echo -off", "fs1:",
                          "echo Starting UEFI Application...", EFI_FILE_NAME]
ARCH: dict[str, QemuItem] = {
    "X86_64": QemuItem("qemu-system-x86_64", "/usr/share/OVMF/OVMF_CODE.fd",
                       "/usr/share/OVMF/OVMF_VARS.fd", "/usr/share/OVMF/UefiShell.iso"),
    "IA32": QemuItem("qemu-system-i386", "/usr/share/edk2/ovmf-ia32/OVMF_CODE.fd",
                     "/usr/share/edk2/ovmf-ia32/OVMF_VARS.fd", "/usr/share/edk2/ovmf-ia32/UefiShell.iso")
}


def qemu_run(
    qemu_path: str,
    rootfs_img: str,
    ovmf_code_path: str,
    ovmf_vars_path: str,
    uefi_shell_path: str,
    networking: bool,
    extra_args: list[str],
):
    command = [
        qemu_path,
        "-drive",
        f"if=pflash,format=raw,index=0,file={ovmf_code_path}",
        "-drive",
        f"if=pflash,format=raw,index=1,file={ovmf_vars_path}",
        "-drive",
        f"format=raw,media=disk,index=2,file={uefi_shell_path}",
        "-drive",
        f"format=raw,media=disk,index=3,file={rootfs_img}",
        "-device",
        "virtio-rng-pci",
        "-serial",
        "file:output.txt"
    ] + extra_args
    if networking:
        command += ["-netdev", "user,id=net0,hostfwd=tcp::12345-:12345",
                    "-device", "virtio-net-pci,netdev=net0,mac=00:00:00:00:00:00"]
    else:
        command += ["-net", "none"]
    subprocess.run(command)


# Crete fat32 rootfs using dd and mtools
def setup_rootfs(tempdir: str, efi_file: str, startup_file: str) -> str:
    rootfs_img = path.join(tempdir, ROOTFS_IMG_NAME)
    subprocess.run(
        ["dd", "if=/dev/zero", f"of={rootfs_img}", "bs=1M", "count=1024"])
    subprocess.run(["mformat", "-i", rootfs_img, "::"])
    subprocess.run(["mcopy", "-i", rootfs_img, efi_file, startup_file, "::"])
    return rootfs_img


# Create startup.nsh file in tempdir
def create_startup_file(tempdir: str, startup_script: str) -> str:
    startup_file_path = path.join(tempdir, STARTUP_FILE_NAME)
    if startup_script:
        shutil.copyfile(startup_script, startup_file_path)
    else:
        with open(startup_file_path, "w") as startup_file:
            startup_file.write("\n".join(DEFAULT_STARTUP_SCRIPT))
    return startup_file_path


# Copy EFI file to tempdir
def copy_efi_file(tempdir: str, efi_file: str) -> str:
    efi_file_path = path.join(tempdir, EFI_FILE_NAME)
    shutil.copyfile(efi_file, efi_file_path)
    return efi_file_path


# Create a copy of OVMF files. This allows launcing multiple instances of qemu
def copy_ovmf_files(tempdir: str, ovmf_code: str, ovmf_vars: str, uefi_shell: str) -> tuple[str, str, str]:
    ovmf_code_path = path.join(tempdir, OVMF_CODE_FILE_NAME)
    ovmf_vars_path = path.join(tempdir, OVMF_VARS_FILE_NAME)
    uefi_shell_path = path.join(tempdir, UEFI_SHELL_FILE_NAME)

    shutil.copyfile(ovmf_code, ovmf_code_path)
    shutil.copyfile(ovmf_vars, ovmf_vars_path)
    shutil.copyfile(uefi_shell, uefi_shell_path)

    return ovmf_code_path, ovmf_vars_path, uefi_shell_path


def parse_args() -> tuple[list[str], list[str]]:
    try:
        break_point = sys.argv.index("--")
        return sys.argv[1:break_point], sys.argv[break_point + 1:]
    except ValueError:
        return sys.argv[1:], []


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
        "-a",
        "--arch",
        choices=ARCH.keys(),
        default="X86_64",
        help="architecture to test on"
    )
    my_parser.add_argument(
        "-c",
        "--code",
        type=str,
        help="path to OVMF Code file",
    )
    my_parser.add_argument(
        "-v",
        "--vars",
        type=str,
        help="path to OVMF Vars file",
    )
    my_parser.add_argument(
        "-s",
        "--shell",
        type=str,
        help="path to UefiShell file",
    )
    my_parser.add_argument(
        "-q",
        "--qemu",
        type=str,
        help="path to qemu executable",
    )
    my_parser.add_argument(
        "-n",
        "--net",
        action='store_true',
        help="enable networking",
    )
    my_parser.add_argument(
        "--startup",
        type=str,
        help="path to startup script",
    )

    return my_parser


def check_dependecies():
    def check_required_deps(bin: str) -> bool:
        if not shutil.which(bin):
            logging.critical(f"command {bin} not found")
            return False
        return True

    def check_optional_deps(bin: str):
        if not shutil.which(bin):
            logging.warning(f"command {bin} not found")

    def check_optional_files(file: str):
        if not path.exists(file):
            logging.warning(f"File {file} not found")

    for val in ARCH.values():
        check_optional_deps(val.qemu)
        check_optional_files(val.ovmf_code)
        check_optional_files(val.ovmf_vars)
        check_optional_files(val.uefi_shell)

    if not (check_required_deps("mformat") and check_required_deps("mcopy")):
        exit(0)


if __name__ == "__main__":
    args, extra_args = parse_args()
    args = setup_cli().parse_args(args)

    check_dependecies()

    qemu = args.qemu if args.qemu else ARCH[args.arch].qemu
    ovmf_code = args.code if args.code else ARCH[args.arch].ovmf_code
    ovmf_vars = args.vars if args.vars else ARCH[args.arch].ovmf_vars
    uefi_shell = args.shell if args.shell else ARCH[args.arch].uefi_shell

    with TemporaryDirectory() as tempdir:
        efi_file = copy_efi_file(tempdir, args.EFI_File)
        startup_file = create_startup_file(tempdir, args.startup)
        rootfs_img = setup_rootfs(tempdir, efi_file, startup_file)
        ovmf_code_path, ovmf_vars_path, uefi_shell_path = copy_ovmf_files(
            tempdir, ovmf_code, ovmf_vars, uefi_shell)
        qemu_run(qemu, rootfs_img, ovmf_code_path,
                 ovmf_vars_path, uefi_shell_path, args.net, extra_args)
