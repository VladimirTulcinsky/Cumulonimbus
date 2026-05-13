#!/usr/bin/env python3
"""Print a formatted table of all available Cumulonimbus labs."""

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROVIDERS = [
    ("AWS",   os.path.join(ROOT, "app", "cumulonimbus", "applications", "aws")),
    ("Azure", os.path.join(ROOT, "app", "cumulonimbus", "applications", "azure")),
]

DIFFICULTY_COLOR = {
    "Beginner":     "\033[32m",   # green
    "Intermediate": "\033[33m",   # yellow
    "Advanced":     "\033[31m",   # red
}
RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
CYAN   = "\033[36m"


def get_difficulty(lab_dir: str) -> str:
    path = os.path.join(lab_dir, "application_configuration.py")
    try:
        m = re.search(
            r'return\s+"(Beginner|Intermediate|Advanced)"',
            open(path).read(),
        )
        return m.group(1) if m else "?"
    except OSError:
        return "?"


def main() -> None:
    filter_provider = sys.argv[1].lower() if len(sys.argv) > 1 else None

    print(f"\n{BOLD}{'LAB ID':<38}  {'PROVIDER':<7}  DIFFICULTY{RESET}")
    print(DIM + "─" * 62 + RESET)

    for provider, base in PROVIDERS:
        if filter_provider and filter_provider != provider.lower():
            continue
        if not os.path.isdir(base):
            continue

        labs = sorted(
            d for d in os.listdir(base)
            if os.path.isdir(os.path.join(base, d))
        )

        print()
        print(f"{BOLD}{CYAN}{provider}{RESET}")

        for lab in labs:
            diff = get_difficulty(os.path.join(base, lab))
            color = DIFFICULTY_COLOR.get(diff, "")
            print(f"  {lab:<36}  {provider:<7}  {color}{diff}{RESET}")

    print()


if __name__ == "__main__":
    main()
