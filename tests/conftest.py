import os

pytest_plugins = ["pytester"]

os.environ.setdefault("EVALCHECK_AUTOWRITE", "0")
