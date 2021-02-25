#!/bin/sh
import sys
import subprocess
import argparse


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--install",
        action="store_true",
        help="Install all dependencies"
    )
    parser.add_argument(
        "-c",
        "--commitlint",
        action="store_true",
        help="Lint commit message"
    )
    parser.add_argument(
        "-l",
        "--lint",
        action="store_true",
        help="Lint Python files"
    )
    parser.add_argument(
        "-d",
        "--dockerlint",
        action="store_true",
        help="Lint Docker file"
    )
    parser.add_argument(
        "-f",
        "--format",
        action="store_true",
        help="Format Python files"
    )
    parser.add_argument(
        "-t",
        "--test",
        action="store_true",
        help="Run Python unit tests"
    )
    parser.add_argument(
        "-p",
        "--prettier",
        action="store_true",
        help="Run Prettier against JSON and MD files"
    )
    if not len(sys.argv) > 1:
        argparse.error(
            "[-] Please specify arguments, use --help for more info.")

    return parser.parse_args()


class MissingDependiesError(Exception):
    pass


def preinstall():
    exit_code = subprocess.call(
        "python3 --version && \
            node --version && \
            yarn --version && \
            pip3 --version && \
            docker --version",
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        shell=True
    )
    if exit_code != 0:
        raise MissingDependiesError("Missing dependencies")


def install():
    preinstall()

    subprocess.call(
        "pip3 install -r requirements.txt && \
            docker pull hadolint/hadolint && \
            yarn",
        shell=True
    )


def lint():
    subprocess.call(
        "find . -type f -name '*.py' | xargs pylint",
        shell=True
    )


def dockerlint():
    subprocess.call(
        "docker run --rm -i hadolint/hadolint < Dockerfile",
        shell=True
    )


def format():
    subprocess.call(
        "autopep8 --in-place --recursive .",
        shell=True
    )


def prettier():
    subprocess.call(
        "yarn prettier --write '**/*.{json,md}'",
        shell=True
    )

def commitlint():
    subprocess.call(
        "yarn commitlint --edit",
        shell=True
    )


def test():
    subprocess.call(
        "python3 -m unittest",
        shell=True
    )


def cli():
    options = get_arguments()
    if options.install:
        install()
    if options.lint:
        lint()
    if options.dockerlint:
        dockerlint()
    if options.format:
        format()
    if options.prettier:
        prettier()
    if options.commitlint:
        commitlint()
    if options.test:
        test()


cli()
