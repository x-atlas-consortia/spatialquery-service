"""
spatialquery.py

Obtains inputs to be used to configure a SpatialQuery Vitessce configuration.

"""
from flask import Blueprint, make_response, jsonify, session, request

from models.datasetwithfiles import DatasetWithFiles
from models.spatialquery_manager import SpatialQueryManager

spatialquery_blueprint = Blueprint('spatialquery', __name__, url_prefix='/spatialquery')

@spatialquery_blueprint.route('/vitessce-config/<datasetid>', methods=['GET'])
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
    spv = SpatialQueryManager(absolute_file_path=dataset_with_files.absolute_file_path)
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

@spatialquery_blueprint.route('/find_fp_knn/<datasetid>', methods=['GET'])
def get_spatialquery_find_fp_knn(datasetid):

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
    spv = SpatialQueryManager(absolute_file_path=dataset_with_files.absolute_file_path)

    celltype = request.args.get('celltype')
    if celltype is None:
        celltype = "podocyte"

    k = request.args.get('k')
    if k is None:
        k = 30
    else:
        k = int(k)

    min_support = request.args.get('min_support')
    if min_support is None:
        min_support = 0.7
    else:
        min_support = float(min_support)

    max_distance = request.args.get('max_distance')
    if max_distance is None:
        max_distance = 20
    else:
        max_distance = float(max_distance)

    dict_response = spv.find_fp_knn(ct=celltype, k=k, min_support=min_support, max_distance=max_distance)
    return make_response(jsonify(dict_response), 200)


