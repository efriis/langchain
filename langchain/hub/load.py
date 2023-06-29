import urllib.error
import urllib.request
from typing import Any, Dict, Optional

from langchain.hub._api import HubApi
from langchain.load.dump import dumps
from langchain.load.load import loads
from langchain.load.serializable import Serializable

OBJECT_PATH = "main.lc.json"

def download(owner: str, repo: str, ref: Optional[str] = None, *, secrets_map: Optional[Dict[str, str]] = None, **kwargs) -> Any:
    # can raise filenotfound error
    api = HubApi(**kwargs)
    resp = api.get_repo_file(owner, repo, OBJECT_PATH, ref)
    content = resp["content"].decode()
    
    return loads(content, secrets_map=secrets_map)

def upload(object: Serializable, owner: str, repo: str, upsert: bool = False, *, autoconfirm: bool = False, **kwargs) -> None:
    # ONLY SUPPORT UPLOAD TO USER - NO ORGS OR SHARED YET
    """
    if repo doesn't exist:
        create repo

    if file exists:
        get sha
        update file
    else:
        create file with contents
    """
    # check if repo exists, get file sha if so
    api = HubApi(**kwargs)

    # check if repo exists
    try:
        api.get_repo(owner, repo)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            # repo doesn't exist, create it
            api.create_repo(owner, repo)
        else:
            raise e
    
    # get existing sha if file exists
    existing_file = api.get_repo_file(owner, repo, OBJECT_PATH)

    # content
    content = dumps(object, pretty=True).encode()

    # if not, create it with file contents
    if existing_file is None:
        api.create_repo_file(owner, repo, OBJECT_PATH, content=content)
    else:
        existing_sha = existing_file["sha"]
        # else update the file
        api.update_repo_file(owner, repo, OBJECT_PATH, content=content, sha=existing_sha)
