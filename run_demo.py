"""
Convenience launcher for the relay server.
"""

import subprocess
import sys


def main():

    subprocess.run(
        [
            sys.executable,
            "server.py"
        ],
        check=True
    )


if __name__ == "__main__":

    main()