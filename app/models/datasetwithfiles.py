"""
DatasetWithFiles: class representing a dataset that combines
the dataset entity with information on files in the
dataset's provenance chain.

"""

from flask import abort, session
import requests

# Helper classes
from .apihelper import ApiHelper
# Represents the app.cfg file
from .appconfig import AppConfig

class DatasetWithFiles:

    def __init__(self, dataset_id:str):

        """
        Store the id of the specified dataset.
        In general, the id of a dataset is not identical to the
        ID of the dataset in the provenance chain to which files
        are linked.
        """

        self.dataset_id = dataset_id
        self.file_uuid = ''
        self.files = []
        self.label_key = ''

        # Build consortium-specific API headers.
        apihelper = ApiHelper()
        # translated consortium string
        self.consortium = apihelper.consortium
        # request headers
        self.headers = apihelper.headers

        """
        The url base for API calls depends on the configuration:
        1. Consortium (HuBMAP or SenNet)
        2. Environment (development or production)
        """
        self.cfg = AppConfig()
        self.urlbase = self.cfg.getfield(key='ENTITY_BASE_URL')

        # Get the entity for the specified dataset.
        self.dataset_entity = self._get_dataset_entity(dataset_id=dataset_id)
        self.dataset_uuid = self.dataset.get('uuid')

        # Search for files in the dataset's provenance chain.
        self._get_files()

    def _get_dataset_entity(self, dataset_id: str) -> dict:
        """
        Obtains the entity object for a dataset.
        :param dataset_id: ID of a dataset
        """
        url = f'{self.urlbase}.{self.consortium}.org/entities/{dataset_id}'
        response = requests.get(url=url, headers=self.headers)

        if response.status_code == 200:
            rjson = response.json()
            entity_type = rjson.get('entity_type')
            if entity_type != 'Dataset':
                abort(400,f'The entity with ID {dataset_id} is not a dataset in {self.consortium}.')

            self.dataset = rjson

            return rjson

        elif response.status_code == 404:
            abort(404, f'No dataset with id {dataset_id} found in provenance for {self.consortium} '
                       f'in environment {self.urlbase}')
        elif response.status_code == 400:
            err = response.json().get('error')
            if 'is not a valid id format' in err:
                # Translate this as a 404, not a 400.
                abort(404, f'No dataset with id {dataset_id} found in provenance for {self.consortium} '
                           f'in environment {self.urlbase}')
            else:
                abort(response.status_code, response.json().get('error'))
        else:
            abort(response.status_code, f'Error after calling /entities GET endpoint in entity-api '
                                        f'for dataset {dataset_id}')

    def _get_files(self):
        """
        Obtains the list of file objects for a dataset.
        In general, the files for a dataset are actually linked to
        a descendant dataset in the specified dataset's provenance chain.
        """

        files = self.dataset_entity.get('files')
        if files is not None and len(files) > 0:
            # Files are linked to the specified dataset.
            self.files = files
        else:

            """
            Loop through the set of the dataset's descendants.
            Identify the published dataset with the latest
            last_modified_timestamp that has files.
            """

            # Get a subset of descendant information.
            url_descendants = f'{self.urlbase}.{self.consortium}.org/descendants-info/{self.dataset_uuid}?include=uuid,status,entity_type,last_modified_timestamp,files'
            response = requests.get(url=url_descendants, headers=self.headers)

            if response.status_code == 200:

                descendants = response.json()
                file_entity = {}
                descendant_timestamp = 0

                for d in descendants:
                    entity_type = d.get('entity_type')

                    if entity_type == 'Dataset':
                        descendant_status = d.get('status')

                        if descendant_status == 'Published':
                            timestamp = d.get('last_modified_timestamp')

                            if timestamp >= descendant_timestamp:
                                files = d.get('files')

                                if files is not None:
                                    file_entity = d


                if file_entity == {}:
                    abort(404,f'No files associated with dataset {self.dataset_id}.')

                self.file_uuid = file_entity.get('uuid')
                self.files = file_entity.get('files')

                # Get the absolute file path to the dataset with the file associations.
                self.absolute_file_path = self._get_absolute_file_path(dataset_uuid=self.file_uuid)

            elif response.status_code == 404:
                abort(404, f'No file associated with dataset {self.dataset_id}.')
            else:
                abort(response.status_code, response.json().get('error'))


    def _get_absolute_file_path(self, dataset_uuid:str):
        """
        Obtains the absolute file path for a dataset.
        :param uuid: uuid for dataset
        """

        # The url base depends on both the consortium and the environment (i.e., development vs production).
        self.cfg = AppConfig()
        self.urlbase = self.cfg.getfield(key='INGEST_BASE_URL')

        url = f'{self.urlbase}.{self.consortium}.org/datasets/{dataset_uuid}/file-system-abs-path'
        response = requests.get(url=url, headers=self.headers)

        if response.status_code == 200:
            rjson = response.json()
            return rjson.get('path')

        elif response.status_code == 404:
            abort(404, f'No absolute file path for dataset with id {dataset_uuid} found in provenance for {self.consortium} '
                       f'in environment {self.urlbase}')
        elif response.status_code == 400:
            err = response.json().get('error')
            if 'is not a valid id format' in err:
                # Translate this as a 404, not a 400.
                abort(404, f'No absolute file path for dataset with id {dataset_uuid} found in provenance for {self.consortium} '
                           f'in environment {self.urlbase}')
            else:
                abort(response.status_code, response.json().get('error'))
        else:
            abort(response.status_code, f'Error after calling /datasets/.../file-system-abs-path GET endpoint in ingest-api '
                                        f'for dataset {dataset_uuid}')