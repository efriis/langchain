import json
import urllib.error
import urllib.request
from base64 import b64decode, b64encode
from typing import Any, Dict, Optional, TypedDict

from langchain.utils import get_from_dict_or_env

"""
Used APIs:
Update a file in repository: PUT /repos/{owner}/{repo}/contents/{filepath}
Get metadata and contents: GET /repos/{owner}/{repo}/contents/{filepath}
Create a repo with contents: 
"""
# KEYS

HUB_KEY = "hub_base_url"
HUB_ENV_KEY = "LANGCHAIN_HUB_BASE_URL"
HUB_DEFAULT = "http://localhost:4000/"

HUB_API_KEY_KEY = "hub_api_key"
HUB_API_KEY_ENV_KEY = "LANGCHAIN_HUB_API_KEY"

API_BASE = "api/v1"
MAIN_BRANCH = "main"

class FileDict(TypedDict):
    sha: str
    content: bytes

class HubApi():
    def __init__(self, **kwargs):
        hub_base = get_from_dict_or_env(kwargs, HUB_KEY, HUB_ENV_KEY, HUB_DEFAULT)
        self.base_url = f"{hub_base}/{API_BASE}"
        self.headers = _get_default_headers(**kwargs)
        self.username: Optional[str] = None

    def _init_user(self):
        if self.username is not None:
            return
        
        path = "user"
        resp = self._request_json(path, method="GET")
        self.username = resp["login"]

    def _request_json(self, path: str, *, method: str = "GET", body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/{path}"
        data = None
        if body:
            data = json.dumps(body).encode()
        req = urllib.request.Request(url, headers=self.headers, method=method, data=data)
        with urllib.request.urlopen(req) as response:
            content = response.read().decode()
            return json.loads(content)
        
    def get_repo(self, owner: str, repo: str):
        path = f"repos/{owner}/{repo}"
        return self._request_json(path, method="GET")
    
    def create_repo(self, owner: str, repo: str, private: bool = False):
      # DOES NOT SUPPORT ORGS YET - ONLY SUPPORTS DEFAULT USER
      # confirm user is username
      self._init_user()
      assert owner == self.username, "Only supports creating repos for the current user at the moment"

      path = f"user/repos"
      body = {
          "name": repo,
          "private": private,
      }
      return self._request_json(path, method="POST", body=body)

    def get_repo_file(self, owner: str, repo: str, filepath: str, ref: Optional[str]=None) -> Optional[FileDict]:
        path = f"repos/{owner}/{repo}/contents/{filepath}"
        if ref:
            path += f"?ref={ref}"

        resp = self._request_json(path, method="GET")
        if isinstance(resp, list):
            # thinks it's a directory
            if len(resp) == 0:
                return None
            raise ValueError(f"Expected file, got directory: {resp}")
        return {
            "sha": resp["sha"],
            "content": b64decode(resp["content"]),
        }
    
    def create_repo_file(self, owner: str, repo: str, filepath: str, content: bytes) -> None:
        path = f"repos/{owner}/{repo}/contents/{filepath}"
        body_dict = {
            "content": b64encode(content).decode(),
        }
        self._request_json(path, method="POST", body=body_dict)

    def update_repo_file(self, owner, repo, filepath, sha: str, content: bytes, **kwargs):
        path = f"repos/{owner}/{repo}/contents/{filepath}"
        body_dict = {
            "sha": sha,
            "content": b64encode(content).decode(),
        }
        self._request_json(path, method="PUT", body=body_dict)

    


def _get_api_key(**kwargs):
    return get_from_dict_or_env(kwargs, HUB_API_KEY_KEY, HUB_API_KEY_ENV_KEY, "")

def _get_default_headers(**kwargs):
    headers = {

      "Content-Type": "application/json"
    }
    hub_api_key = _get_api_key(**kwargs)
    if hub_api_key:
        headers["Authorization"] = f"token {hub_api_key}"
    return headers
