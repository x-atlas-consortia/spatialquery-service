from flask import Blueprint, request, render_template, redirect, session, make_response, abort
# Entity-api functions
from models.entity import Entity

get_uuuids_blueprint = Blueprint('get_uuids', __name__, url_prefix='/get-uuids')

@get_uuuids_blueprint.route('', methods=['POST','GET'])
def get_uuuids():

    consortium = session.get('consortium')
    datasetid = session.get('datasetid')
    print('datasetid:', datasetid)

    # Obtain dataset information from provenance.
    # First, obtain the authentication token from the session cookie.
    if 'groups_token' in session:
        token = session.get('groups_token')
    else:
        abort(401)

    dataset_entity = Entity(consortium=consortium, token=token)
    uuid = dataset_entity.get_dataset_uuid(datasetid)
    msg = {'dataset id': datasetid, 'uuid': uuid}

    return make_response(msg, 200)
