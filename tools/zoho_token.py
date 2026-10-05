"""One-time helper: turn a Zoho "Self Client" grant code into a refresh token, and test it.

    python tools/zoho_token.py

Run it on your own computer (not in CI). It asks for the Client ID, Client Secret and the grant
code you generated in https://api-console.zoho.eu, prints the refresh token, and checks that it can
read Job Openings. Nothing is written to disk — paste the values into GitHub:
Settings → Secrets and variables → Actions → New repository secret.
"""
import getpass
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

ACCOUNTS = "https://accounts.zoho.eu"            # EU data centre (zohorecruit.eu)
API = "https://recruit.zoho.eu/recruit/v2"


def post(url: str, fields: dict) -> dict:
    req = urllib.request.Request(url, data=urllib.parse.urlencode(fields).encode(), method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:300]}"}


def main() -> None:
    client_id = (os.environ.get("ZOHO_CLIENT_ID") or input("Client ID: ")).strip()
    # Hidden prompts on Windows don't accept Ctrl+V. Alternatives: set ZOHO_CLIENT_SECRET in the
    # environment first, or run with --show to paste it visibly (then clear the terminal: cls).
    if os.environ.get("ZOHO_CLIENT_SECRET"):
        client_secret = os.environ["ZOHO_CLIENT_SECRET"]
    elif "--show" in sys.argv:
        client_secret = input("Client Secret (visible — clear the terminal afterwards): ")
    else:
        client_secret = getpass.getpass("Client Secret (hidden; if pasting doesn't work, re-run with --show): ")
    client_secret = client_secret.strip()
    if not client_secret:
        print("No client secret entered. Re-run with:  python tools/zoho_token.py --show")
        return
    print(f"(client secret received: {len(client_secret)} characters)")
    code = input("Grant code (from 'Generate Code', valid a few minutes): ").strip()

    tokens = post(f"{ACCOUNTS}/oauth/v2/token", {
        "grant_type": "authorization_code", "client_id": client_id,
        "client_secret": client_secret, "code": code,
    })
    if "refresh_token" not in tokens:
        print("\nFailed:", tokens.get("error", tokens))
        print("Common causes: the code expired (generate a new one), wrong data centre "
              "(use api-console.zoho.eu for .eu accounts), or the code was already used.")
        return

    # Prove it works: read one page of Job Openings.
    req = urllib.request.Request(f"{API}/Job_Openings?per_page=5",
                                 headers={"Authorization": f"Zoho-oauthtoken {tokens['access_token']}"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8")
        data = json.loads(raw) if raw.strip() else {}
        jobs = data.get("data") or []
        print(f"\nAPI test OK — read {len(jobs)} job opening(s), e.g.: "
              + ", ".join(j.get("Posting_Title") or j.get("Job_Opening_Name") or "?" for j in jobs[:3]))
    except urllib.error.HTTPError as e:
        print(f"\nToken created, but the API test failed (HTTP {e.code}): "
              f"{e.read().decode('utf-8', 'replace')[:300]}")
        print("Check the scope used when generating the code (ZohoRecruit.modules.jobopening.READ).")

    print("\nAdd these three repository secrets on GitHub "
          "(Settings → Secrets and variables → Actions → New repository secret):\n")
    print(f"  ZOHO_CLIENT_ID      = {client_id}")
    print("  ZOHO_CLIENT_SECRET  = (the secret you just typed)")
    print(f"  ZOHO_REFRESH_TOKEN  = {tokens['refresh_token']}")
    print("\nKeep the refresh token private: it gives read access to your Zoho Recruit job openings.")


if __name__ == "__main__":
    main()
