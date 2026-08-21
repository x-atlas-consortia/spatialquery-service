"""
spatialqueryvitessce_inputs.py

Obtains inputs to be used to configure a SpatialQuery Vitessce configuration:
1. Locations of secondary analysis files:
   a. AnnData
   b. Zarr
2. List of cell types in the AnnData file.

"""
from flask import Blueprint, request, render_template, redirect, session, make_response, abort
import pandas as pd
import json

from models.entity import Entity
from models.anndata import Anndata

spatialqueryvitessceinputs_blueprint = Blueprint('spatialqueryvitessce_inputs', __name__, url_prefix='/spatialqueryvitessce-inputs')

@spatialqueryvitessceinputs_blueprint.route('/<datasetid>', methods=['POST','GET'])
def get_spatialqueryvitessce_inputs(datasetid):

    # Get consortium from the session.
    consortium = session.get('consortium')

    # Obtain dataset information from provenance.
    # First, obtain the authentication token from the session cookie.
    if 'groups_token' in session:
        token = session.get('groups_token')
    else:
        abort(401)

    # Get the UUID for the dataset.
    print(f'Getting UUID for dataset {datasetid}')
    dataset_entity = Entity(consortium=consortium, token=token)
    uuid = dataset_entity.get_dataset_uuid(datasetid)

    # Hard-coded for demo.
    uuid = '72fd0d8256cd9d9e9d0c75ed7b4431cc'

    """
    Load spatial transcriptomics data, using file paths
    calculated from the uuid.
    """
    anndata = Anndata(dataset_uuid=uuid)

    return make_response("get_spatialqueryvitessce_inputs+", 200)
