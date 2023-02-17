#!/usr/bin/env python3
"""
The script counts dependencies of current Go repository.
Uses "go mod graph" to build dependencies tree.
"""

import argparse
from dataclasses import dataclass
import os
from pathlib import Path
import subprocess


LOGFILE = "dependencies.log"
GOLANG_PATTERN = "github.com/golang/"
GO_MOD_COMMAND = "go mod graph"


@dataclass
class Token:
    package: str
    dependency: str
    package_version: [str, None]
    dependency_version: [str, None]


def prepare_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dir", type=str, help="Path to the directory where 'go mod graph' should be run",
                        default=os.curdir)
    parser.add_argument("-l", "--logfile", type=str, help="Path to the log file including its name", default=LOGFILE)
    return parser.parse_args()


def log_parser(string: str):
    package_full, dependency_full = string.split()
    package_with_ver = package_full.split("@")
    package_name = package_with_ver[0]
    package_version = package_with_ver[1] if len(package_with_ver) > 1 else None
    dependency_name, dependency_version = dependency_full.split("@")
    return Token(
        package=package_name,
        dependency=dependency_name,
        package_version=package_version,
        dependency_version=dependency_version
    )


if __name__ == "__main__":
    args = prepare_args()
    log_file = Path(os.path.expanduser(args.logfile))
    repo_dir = Path(os.path.expanduser(args.dir))
    subprocess.check_output(f"{GO_MOD_COMMAND} > {log_file.absolute()}", shell=True, cwd=repo_dir.absolute())
    with open(log_file, "r") as datafile:
        packages = set()
        for link in datafile:
            token = log_parser(link)
            if GOLANG_PATTERN not in token.package:
                packages.add(token.package)
                if GOLANG_PATTERN not in token.dependency:
                    packages.add(token.dependency)
        for p in packages:
            print(p)
        print("Total:", len(packages))
