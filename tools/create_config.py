import sys


sys.path.insert(0, "src")

from config_types import Config
from consts import CONFIG_DIR


file = CONFIG_DIR / "config.toml"
if Config.create(file):
    print(f"Config file created successfully at {file}")
else:
    print("Config file already exists")
