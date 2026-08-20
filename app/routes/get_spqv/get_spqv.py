"""
get_spqv.py

Obtains information for the SpatialQuery Vitessce plug-in.

"""
from flask import Blueprint, request, render_template, redirect, session, make_response, abort
import pandas as pd
import json

from models.entity import Entity
from models.anndata import Anndata
from models.spatialquery_vitessce import SpatialQueryVitessce

get_spqv_blueprint = Blueprint('get_spqv', __name__, url_prefix='/get-spqv')

@get_spqv_blueprint.route('', methods=['POST','GET'])
def get_spatialquery_vitessce():

    # Get input from the session.
    consortium = session.get('consortium')
    datasetid = session.get('datasetid')
    celltype = session.get('celltype')

    # Obtain dataset information from provenance.
    # First, obtain the authentication token from the session cookie.
    if 'groups_token' in session:
        token = session.get('groups_token')
    else:
        abort(401)

    # Get the UUID for the dataset.
    #dataset_entity = Entity(consortium=consortium, token=token)
    #uuid = dataset_entity.get_dataset_uuid(datasetid)

    # Hard-coded for demo.
    uuid = '72fd0d8256cd9d9e9d0c75ed7b4431cc'

    """
    Load spatial transcriptomics data, using file paths
    calculated from the uuid.
    """
    anndata = Anndata(dataset_uuid=uuid)

    """
    Initialize SpatialQuery.
    """
    spv = SpatialQueryVitessce(anndata=anndata,celltype=celltype)

    """
    Identification of Frequent Patterns Around an 
    Anchor Cell Type of Interest with find_fp_knn
    """
    #df_fp_knn = spv.find_fp_knn()
    vcwidget = spv.get_vitessce_widget()
    print(json.dumps(vcwidget))

    #msg = {'dataset id': datasetid, 'celltype':celltype, 'uuid': uuid, 'number of cells': str(anndata.num_cells)}

    return make_response(vcwidget, 200)
