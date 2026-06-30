#!/usr/bin/env python3
"""快速入口:等同 `python -m worldcup_fate`。

範例:
    python divine.py 阿根廷 法國 --stage 決賽
"""

import sys

from worldcup_fate.cli import main

if __name__ == "__main__":
    sys.exit(main())
