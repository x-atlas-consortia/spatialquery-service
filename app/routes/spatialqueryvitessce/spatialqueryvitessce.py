"""
spatialqueryvitessce_inputs.py

Obtains inputs to be used to configure a SpatialQuery Vitessce configuration.

"""
from flask import Blueprint, make_response, jsonify, session, request

from models.datasetwithfiles import DatasetWithFiles
from models.spatialqueryvitessce_manager import SpatialQueryVitessceManager

spatialqueryvitessce_blueprint = Blueprint('spatialqueryvitessce', __name__, url_prefix='/spatialqueryvitessce')

@spatialqueryvitessce_blueprint.route('/vitessce-config/<datasetid>', methods=['GET'])
def get_spatialqueryvitessce_config(datasetid):

    """
    Obtain for the specified dataset id:
    1. uuid
    2. uuid for the dataset in the dataset's provenance chain that
       has secondary analysis files
    3. absolute file path to the secondary analysis files
    """
    print(f'Getting file information for dataset {datasetid}')
    dataset_with_files = DatasetWithFiles(dataset_id=datasetid)

    """
    Initialize SpatialQuery using the secondary analysis files.
    """
    spv = SpatialQueryVitessceManager(absolute_file_path=dataset_with_files.absolute_file_path)
    vcwidget = spv.get_vitessce_widget()

    dict_response = {
        "dataset_info":{
            "id": datasetid,
            "uuid": dataset_with_files.dataset_uuid
        },
        "file_info":{
            "file_dataset_uuid":dataset_with_files.file_uuid,
            #"files":dataset_with_files.files,
            "absolute_file_path":dataset_with_files.absolute_file_path
        },
        "config":vcwidget
    }

    return make_response(jsonify(dict_response), 200)

