#!/bin/python3
import argparse
import subprocess
import shutil
import sys
from os import path
from tempfile import TemporaryDirectory

EFI_FILE_NAME: str = "run.efi"
STARTUP_FILE_NAME: str = "startup.nsh"
ROOTFS_IMG_NAME: str = "rootfs.img"
QEMU_BINARY_NAME: str = "qemu-system-x86_64"
OVMF_CODE_FILE_NAME: str = "OVMF_CODE.fd"
OVMF_VARS_FILE_NAME: str = "OVMF_VARS.fd"
UEFI_SHELL_FILE_NAME: str = "UefiShell.iso"


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
        f"if=pflash,format=raw,index=0,file={ovmf_code_path},readonly=on",
        "-drive",
        f"if=pflash,format=raw,index=1,file={ovmf_vars_path},readonly=on",
        "-drive",
        f"format=raw,index=2,file={uefi_shell_path}",
        "-drive",
        f"file={rootfs_img},format=raw,media=disk,index=3",
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
        "-s",
        "--shell",
        type=str,
        help="path to UefiShell file",
        default="/usr/share/OVMF/UefiShell.iso",
    )
    my_parser.add_argument(
        "-q",
        "--qemu",
        type=str,
        help="path to qemu executable",
        default=QEMU_BINARY_NAME
    )
    my_parser.add_argument(
        "-n",
        "--net",
        action='store_true',
        help="enable networking",
    )

    return my_parser


# Crete fat32 rootfs using dd and mtools
def setup_rootfs(tempdir: str, efi_file: str, startup_file: str) -> str:
    rootfs_img = path.join(tempdir, ROOTFS_IMG_NAME)
    subprocess.run(
        ["dd", "if=/dev/zero", f"of={rootfs_img}", "bs=1M", "count=1024"])
    subprocess.run(["mformat", "-i", rootfs_img, "::"])
    subprocess.run(["mcopy", "-i", rootfs_img, efi_file, startup_file, "::"])
    return rootfs_img


# Create startup.nsh file in tempdir
def create_startup_file(tempdir: str) -> str:
    startup_file_path = path.join(tempdir, STARTUP_FILE_NAME)
    with open(startup_file_path, "w") as startup_file:
        lines = ["@echo -off", "fs1:",
                 "echo Starting UEFI Application...", f"{EFI_FILE_NAME} -v --sequential --staticlink"]
        startup_file.write("\n".join(lines))
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


if __name__ == "__main__":
    args, extra_args = parse_args()
    args = setup_cli().parse_args(args)

    with TemporaryDirectory() as tempdir:
        efi_file = copy_efi_file(tempdir, args.EFI_File)
        startup_file = create_startup_file(tempdir)
        rootfs_img = setup_rootfs(tempdir, efi_file, startup_file)
        ovmf_code_path, ovmf_vars_path, uefi_shell_path = copy_ovmf_files(
            tempdir, args.code, args.vars, args.shell)

        qemu_run(args.qemu, rootfs_img, ovmf_code_path,
                 ovmf_vars_path, uefi_shell_path, args.net, extra_args)
