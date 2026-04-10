import os
from pathlib import Path

from dotenv import load_dotenv

dotenv_path = Path(".env")
load_dotenv(dotenv_path=dotenv_path)

env = os.getenv("ENV_MODE", "dev")
base_host = os.getenv("BASE_HOST", "http://127.0.0.1:18000")

if env == "prod":
    from .prod import ProdConfig as Config
else:
    from .dev import DevConfig as Config

ConfigClass = Config()
ConfigClass.docs_config["servers"] = [{"url": base_host}]
