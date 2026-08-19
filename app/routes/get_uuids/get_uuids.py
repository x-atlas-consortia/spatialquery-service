from flask import Blueprint, request, render_template, redirect, session, make_response

get_uuuids_blueprint = Blueprint('get_uuids', __name__, url_prefix='/get-uuids')

@get_uuuids_blueprint.route('', methods=['POST','GET'])
def get_uuuids():
    return make_response('YOU ARE IN get_uuids', 200)
