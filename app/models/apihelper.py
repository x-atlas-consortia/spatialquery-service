"""
Helper class that provides urls and headers for calls to consortium APIs.
"""
from flask import abort, session
# Helper class
# Represents the app.cfg file
from .appconfig import AppConfig

class ApiHelper:

    def __init__(self):

        # Get consortium from the session.
        consortium = session.get('consortium')

        # Obtain the authentication token from the session.
        if 'groups_token' in session:
            self.token = session.get('groups_token')
        else:
            abort(401)

        # Translate context into consortium.
        if consortium == "CONTEXT_HUBMAP":
            self.consortium = "hubmapconsortium"
        elif consortium == "CONTEXT_SENNET":
            self.consortium = 'sennetconsortium'
        else:
            abort(400,f'Invalid consortium: {consortium}')

        # Build consortium-specific header.
        self.cfg = AppConfig()
        self.headers = {'Accept': 'application/json',
                        'Content-Type': 'application/json'}
        if self.consortium == 'sennetconsortium':
            self.headers['X-SenNet-Application'] = 'portal-ui'

        # The bearer token in the configuration file should be the globus_group key from the
        # info cookie set by the consortium application:
        # 1. HuBMAP - as a client cookie. (Use the Ingest UI.)
        # 2. SenNet - as a base64-encoded server cookie.

        self.headers['Authorization'] = f'Bearer {self.token}'