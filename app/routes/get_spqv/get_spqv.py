"""
get_spqv.py

Obtains information for the SpatialQuery Vitessce plug-in.

"""
from flask import Blueprint, request, render_template, redirect, session, make_response, abort
# Entity-api functions
from models.entity import Entity
from models.anndata import Anndata

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
    dataset_entity = Entity(consortium=consortium, token=token)
    uuid = dataset_entity.get_dataset_uuid(datasetid)

    """
    Load spatial transctomics data, using relative file paths
    calculated from the uuid.
    """
    anndata = Anndata(dataset_uuid=uuid)

    msg = {'dataset id': datasetid, 'celltype':celltype, 'uuid': uuid}

    return make_response(msg, 200)
