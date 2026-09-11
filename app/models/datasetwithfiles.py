"""
DatasetWithFiles: class representing a dataset in a consortium that combines
the dataset's entity with information on files in the
dataset's provenance chain.

In general, the ID of a dataset obtained from a portal
is not identical to the ID of the dataset in the provenance chain
to which files are linked. Files are usually linked to one of the
descendant datasets.

Example:
1. The user wants to analyze dataset with consortium ID HBM1 from the portal.
2. HBM1 has descendants with consortium IDs HBM2, HBM3, HBM4, HBM5, and HBM6.
3. Secondary analysis files are stored in the Globus path starting with the
   uuid for the descendant dataset with consortium ID HBM6-- i.e.,
   /uuid6/secondary_analysis.h5ad and /uuid6/secondary_analysis_zarr

For this case, the DatasetWithFiles object will contain information
about dataset with consortium ID HBM1 and the files linked to the
dataset with consortium ID HBM6.

This class assumes that it is initialized with a consortium ID, because
consortium IDs are visible in the Data Portal.

To generalize for initialization with a uuid, use uuid-api instead
of the entity-api.

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
        :param dataset_id: consortium ID of a dataset.

        """

        # consortium id
        self.dataset_id = dataset_id
        # uuid
        self.file_uuid = ''
        # list of paths to secondary analysis files
        self.files = []
        # label_key used in SpatialQuery initialization
        self.label_key = ''

        # Build consortium-specific API headers.
        apihelper = ApiHelper()
        # translated consortium string used in API calls
        self.consortium = apihelper.consortium
        # request headers used in API calls
        self.headers = apihelper.headers

        """
        The url base for API calls depends on the configuration:
        1. Consortium (HuBMAP or SenNet)
        2. Environment (development or production)
        
        """
        self.cfg = AppConfig()
        # Assumes use of entity-api. Change if using uuid-api.
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
                """
                When working with consortium IDs from the Data Portal, it
                is common for a user to provide the consortium ID for 
                an entity other than the dataset--e.g., for a sample.
                """
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

                # Entity that contains files
                file_entity = {}
                # for sorting
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
        Obtains the absolute file path for a dataset, using the
        ingest-api.

        :param dataset_uuid: uuid for dataset
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