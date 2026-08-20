# Class representing interactions with the entity-api.

from flask import abort, session
import requests

# Helper classes
# Represents the app.cfg file
from .appconfig import AppConfig


class Entity:

    def __init__(self,consortium: str, token: str):
        """
        :type consortium: consortium identifier
        :param token: globus groups_token for the consortium's entity-api.

        """
        if consortium == "CONTEXT_HUBMAP":
            urlconsortium = "hubmapconsortium"
        elif consortium == "CONTEXT_SENNET":
            urlconsortium = 'sennetconsortium'
        else:
            abort(400,f'Invalid consortium: {consortium}')

        self.consortium = urlconsortium

        # Build elements of endpoint url and header, reading from the configuration file.
        self.cfg = AppConfig()
        # The url base depends on both the consortium and the enviroment (i.e., development vs production).
        self.urlbase = self.cfg.getfield(key='ENTITY_BASE_URL')
        self.headers = {'Accept': 'application/json',
                        'Content-Type': 'application/json'}
        if self.consortium == 'sennetconsortium':
            self.headers['X-SenNet-Application'] = 'portal-ui'

        # The bearer token in the configuration file should be the globus_group key from the
        # info cookie set by the consortium application:
        # 1. HuBMAP - as a client cookie. (Use the Ingest UI.)
        # 2. SenNet - as a base64-encoded server cookie.
        self.token = token

        self.headers['Authorization'] = f'Bearer {self.token}'

    def get_dataset_uuid(self, datasetid:str) -> dict:
        """
        Searches for the uuid of a dataset in a consortium, using the entity-api.
        :param datasetid: dataset id
        :return: if there is a dataset entity with id=datasetid, the uuid.
        """
        url = f'{self.urlbase}.{self.consortium}.org/entities/{datasetid}'
        response = requests.get(url=url, headers=self.headers)

        if response.status_code == 200:
            rjson = response.json()
            entity_type = rjson.get('entity_type')
            print('entity_type:', entity_type)
            if entity_type != 'Dataset':
                abort(400,f'The entity with ID {datasetid} is not a dataset in {self.consortium}.')

            uuid = rjson.get('uuid')
            return uuid


        elif response.status_code == 404:
            abort(404, f'No dataset with id {datasetid} found in provenance for {self.consortium} '
                       f'in environment {self.urlbase}')
        elif response.status_code == 400:
            err = response.json().get('error')
            if 'is not a valid id format' in err:
                # Translate this as a 404, not a 400.
                abort(404, f'No dataset with id {datasetid} found in provenance for {self.consortium} '
                           f'in environment {self.urlbase}')
            else:
                abort(response.status_code, response.json().get('error'))
        else:
            abort(response.status_code, f'Error after calling /entities GET endpoint in entity-api '
                                        f'for dataset {datasetid}')



