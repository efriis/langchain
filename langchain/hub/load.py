import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional

from langchain.load.load import loads
from langchain.load.serializable import Serializable
from langchain.utils import get_from_dict_or_env

HUB_KEY = "hub_base_url"
HUB_ENV_KEY = "HUB_BASE_URL"
HUB_DEFAULT = "http://localhost:4000/"

HUB_API_KEY_KEY = "chainhub_api_key"
HUB_API_KEY_ENV_KEY = "CHAINHUB_API_KEY"

MAIN_BRANCH = "main"
OBJECT_PATH = "object.lc.json"



def download(path: str, ref: str = MAIN_BRANCH, *, secrets_map: Optional[Dict[str, str]] = None, **kwargs) -> Any:
    hub_base_url = get_from_dict_or_env(kwargs, HUB_KEY, HUB_ENV_KEY, HUB_DEFAULT)
    url = f"{hub_base_url}{path}/raw/branch/{ref}/{OBJECT_PATH}"

    # TODO(erick): handle errors
    with urllib.request.urlopen(url) as response:
        content = response.read().decode()
        return loads(content, secrets_map=secrets_map)
