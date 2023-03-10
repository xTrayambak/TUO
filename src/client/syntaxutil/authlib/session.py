import hashlib
import requests

from src.client.shared import DATA_PROVIDER, SYNTAX_AUTHENTICATION_PROVIDER
from src.log import *

# BUG-006: SyntaxUtil uses MD5, which is an obsolete hashing algorithm and has been succeeded by SHA256.
hasher = hashlib.sha256()

class Session:
    def __init__(self):
        self.requests = []
        self.authenticated = False

    def authenticate(self, instance, token: str = ""):
        warn('Not implemented yet.', 'Worker/SyntaxAuthLib'); return -1

        log("Asking server to start session.", "Worker/SyntaxAuthLib")
        start_flag = requests.get(
            'https://urmom.lol' + "/api/v2/session/instantiate",
            headers = {
                'User-Agent': 'The Untold Odyssey Client',
                'Source': 'https://github.com/xTrayambak/TheUntoldOdyssey_Client'
            }
        ).json()

        if start_flag['result'] == True:
            log("Server has let us open a session!", "Worker/SyntaxAuthLib")
        else:
            warn("Server has declined the authentication request.", "Worker/SyntaxAuthLib")

        hasher.update(instance.version.encode("utf-8"))
        client_hash = f"{hasher.hexdigest()}"

        log(f"Client hash is {client_hash}, asking server to verify.", "Worker/SyntaxAuthLib")

    def get_auth_server_status(self):
        try:
            data = requests.get(
                SYNTAX_AUTHENTICATION_PROVIDER
            ).json()
        except Exception as exc:
            warn(f"An error occured whilst connecting to the authentication provider.\n{exc}")
            data = {
                "status": "NO.",
                "query-params": {}
            }

        return data

    def send_crash_report(self, crashData: dict):
        try:
            data = requests.post(
                DATA_PROVIDER + "/api/v3/telemetry/crash",
                json = data
            )
        except Exception as exc:
            warn(f"An error occured whilst sending telemetry data!\n{exc}", "Worker/Telemetry")
