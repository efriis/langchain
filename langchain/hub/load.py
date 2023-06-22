import importlib
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from langchain.load.load import loads
from langchain.load.serializable import Serializable

HUB_BASE_URL = "http://localhost:3000/"


def _hub_url_from_path(path: str) -> str:
    url = HUB_BASE_URL + path + "/raw/branch/main/object.json"
    return url

import urllib.request


def load_from_hub(path: str, *, secrets_map: Optional[Dict[str, str]] = None) -> Any:
    url = _hub_url_from_path(path)

    # TODO(erick): handle errors
    with urllib.request.urlopen(url) as response:
        content = response.read().decode()
        return loads(content, secrets_map=secrets_map)
