"""
Globus auth routes.

"""

from flask import Blueprint, request, redirect, session, abort
from globus_sdk import AccessTokenAuthorizer, AuthClient, ConfidentialAppAuthClient


# Helper classes
from models.appconfig import AppConfig


def get_user_info(token):
    auth_client = AuthClient(authorizer=AccessTokenAuthorizer(token))
    return auth_client.oauth2_userinfo()


def load_app_client(consortium: str) -> ConfidentialAppAuthClient:

    """
    Initiates a Globus app client, based on the consortium.
    :param consortium: identifies a Globus environment
    """
    cfg = AppConfig()

    if consortium == 'CONTEXT_HUBMAP':
        globus_client = cfg.getfield(key='GLOBUS_HUBMAP_CLIENT')
        globus_secret = cfg.getfield(key='GLOBUS_HUBMAP_SECRET')
    elif consortium == 'CONTEXT_SENNET':
        globus_client = cfg.getfield(key='GLOBUS_SENNET_CLIENT')
        globus_secret = cfg.getfield(key='GLOBUS_SENNET_SECRET')
    else:
        msg = f'Unknown consortium: {consortium}. Check the configuration file.'
        abort(400, msg)

    return ConfidentialAppAuthClient(globus_client, globus_secret)


login_blueprint = Blueprint('login', __name__, url_prefix='/login')

@login_blueprint.route('', methods=['GET'])
def login():
    """
    Login via Globus Auth for SpatialQuery workflows.

    This route is invoked twice for a workflow.

    1. Before authentication to Globus,
       a. The Globus Auth session has no value for the "state" argument of the request.
       b. The Globus environment (consortium) and donor id are stored as session variables.
       c. After establishing the appropriate client, the route executes oauth2_start_flow, which redirects
          first to Globus oauth and then back to itself
    2. After authentication in Globus,
       a. The Globus Auth session has a value for the "code" argument of the request that can be
          exchanged for tokens.
       b. The Globus environment (consortium) and donorid are returned in the "state" argument of the
          request.

    """

    # Clear messages.
    if 'flashes' in session:
        session['flashes'].clear()

    # Obtain state variables.
    # Assumption: all parameters are available from the form that authenticates.

    if 'state' in request.args:
        # Globus environment
        consortium = request.args.get('state').split(' ')[0]
        # Dataset
        datasetid = request.args.get('state').split(' ')[1]
        # service endpoint path
        endpoint = request.args.get('state').split(' ')[2]
        # SpatialQuery parameters
        ct = request.args.get('state').split(' ')[3]
        k = request.args.get('state').split(' ')[4]
        min_support = request.args.get('state').split(' ')[5]
        max_distance = request.args.get('state').split(' ')[6]
        min_size = request.args.get('state').split(' ')[7]
        if_display = request.args.get('state').split(' ')[8]
        figsize_width = request.args.get('state').split(' ')[9]
        figsize_height = request.args.get('state').split(' ')[10]
        return_cellID = request.args.get('state').split(' ')[11]
        return_grid = request.args.get('state').split(' ')[12]
        n_points = request.args.get('state').split(' ')[13]
        seed = request.args.get('state').split(' ')[14]


    else:
        consortium = session['consortium']
        datasetid = session['datasetid']
        endpoint = session['endpoint']
        ct = session['ct']
        k = session['k']
        min_support = session['min_support']
        max_distance = session['max_distance']
        min_size = session['min_size']
        if_display = session['if_display']
        figsize_width = session['figsize_width']
        figsize_height = session['figsize_height']
        return_cellID = session['return_cellID']
        return_grid = session['return_grid']
        n_points = session['n_points']
        seed = session['seed']

    client = load_app_client(consortium)

    # The Globus Auth session will redirect to this route.
    redirect_uri = f'http://localhost:5000/login'
    client.oauth2_start_flow(redirect_uri, refresh_tokens=True)

    # If there's no "code" argument in the request object, then this is the first execution of the route.
    # Redirect out to Globus Auth, extracting parameters from the state key.
    if 'code' not in request.args:
        state = (f'{session["consortium"]} '
                 f'{session["datasetid"]} '
                 f'{session["endpoint"]} '
                 f'{session["ct"]} '
                 f'{session["k"]} '
                 f'{session["min_support"]} '
                 f'{session["max_distance"]} '
                 f'{session["min_size"]} '
                 f'{session["if_display"]} '
                 f'{session["figsize_width"]} '
                 f'{session["figsize_height"]} '
                 f'{session["return_cellID"]} '
                 f'{session["return_grid"]} '
                 f'{session["n_points"]} '
                 f'{session["seed"]} '
                 )
        params: dict = {"scope": "openid profile email"
                                 " urn:globus:auth:scope:transfer.api.globus.org:all"
                                 " urn:globus:auth:scope:auth.globus.org:view_identities"
                                 " urn:globus:auth:scope:groups.api.globus.org:all",
                        "state": state}
        auth_uri = client.oauth2_get_authorize_url(query_params=params)
        return redirect(auth_uri)

    # If the request contains a code argument, then this is the second execution of the route, returning from
    # Globus Auth. Exchange the auth code for a token.
    else:
        auth_code = request.args.get('code')
        token_response = client.oauth2_exchange_code_for_tokens(auth_code)

        # Get all Bearer tokens
        auth_token = token_response.by_resource_server['auth.globus.org']['access_token']
        # nexus_token = token_response.by_resource_server['nexus.api.globus.org']['access_token']
        # transfer_token = token_response.by_resource_server['transfer.api.globus.org']['access_token']
        groups_token = token_response.by_resource_server['groups.api.globus.org']['access_token']
        # Also get the user info (sub, email, name, preferred_username) using the AuthClient with the auth token
        user_info = get_user_info(auth_token)

        session['groups_token'] = groups_token
        session['consortium'] = consortium
        session['userid'] = user_info.get('preferred_username')
        session['datasetid'] = datasetid
        session['endpoint'] = endpoint
        session['ct'] = ct
        session['k'] = k
        session['min_support'] = min_support
        session['max_distance'] = max_distance
        session['min_size'] = min_size
        session['if_display'] = if_display
        session['figsize_width'] = figsize_width
        session['figsize_height'] = figsize_height
        session['return_cellID'] = return_cellID
        session['return_grid'] = return_grid
        session['n_points'] = n_points
        session['seed'] = seed


        # Redirect to the page that obtains information for the SpatialQuery/Vitessce integration.

        if endpoint == 'vitessce-config':
            return redirect(f'/spatialquery/vitessce-config/{datasetid}')
        elif endpoint == 'find_fp_knn':
            return redirect(
                f'/spatialquery/{endpoint}/{datasetid}'
                f'?ct={ct}'
                f'&k={k}'
                f'&min_support={min_support}'
                f'&max_distance={max_distance}'
                )
        elif endpoint == 'find_fp_dist':
            return redirect(
                f'/spatialquery/{endpoint}/{datasetid}'
                f'?ct={ct}'
                f'&max_distance={max_distance}'
                f'&min_size={min_size}'
                f'&min_support={min_support}'
                )
        elif endpoint == 'find_patterns_grid':
            return redirect(
                f'/spatialquery/{endpoint}/{datasetid}'
                f'?max_distance={max_distance}'
                f'&min_size={min_size}'
                f'&min_support={min_support}'
                f'&if_display={if_display}'
                f'&figsize=({figsize_width},{figsize_height})'
                f'&return_cellID={return_cellID}'
                f'&return_grid={return_grid}'
                )
        elif endpoint == 'find_patterns_rand':
            return redirect(
                f'/spatialquery/{endpoint}/{datasetid}'
                f'?max_distance={max_distance}'
                f'&n_points={n_points}'
                f'&min_support={min_support}'
                f'&min_size={min_size}'
                f'&if_display={if_display}'
                f'&figsize=({figsize_width},{figsize_height})'
                f'&return_cellID={return_cellID}'
                f'&seed={seed}'
            )


