#!/usr/bin/env python3

import sys
import cumulonimbus.global_variables as global_variables

from cumulonimbus.__main__ import run_from_cli

if __name__ == "__main__":
    global_variables.init()
    sys.exit(run_from_cli())
