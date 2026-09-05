"""
Index route that:
1. obtains Globus environment, dataset id, and SpatialQuery API parameters from a form
2. authenticates to Globus
"""

from flask import Blueprint, request, render_template, redirect, session, make_response

globus_blueprint = Blueprint('globus', __name__, url_prefix='/')

@globus_blueprint.route('/', methods=['GET','POST'])

def globus():

    """
    Index route that attempt to authenticate to a Globus consortium.
    """

    if request.method == 'POST':

        # Globus environment
        consortium = request.form.get('consortium')

        # service endpoint path
        endpoint = request.form.get('endpoint')

        # SpatialQuery parameters
        datasetid = request.form.get('datasetid')
        ct = request.form.get('ct')
        k = request.form.get('k')
        min_support = request.form.get('min_support')
        max_distance = request.form.get('max_distance')
        min_size = request.form.get('min_size')
        if_display = request.form.get('if_display')
        figsize_width = request.form.get('figsize_width')
        figsize_height = request.form.get('figsize_height')
        return_cellID = request.form.get('return_cellID')
        return_grid = request.form.get('return_grid')
        n_points = request.form.get('n_points')
        seed = request.form.get('seed')


        # Get the consortium from the request.
        if consortium.upper() not in ['HUBMAP', 'SENNET']:
            return make_response(f'Invalid consortium: {consortium}', 400)
        consortium = consortium.upper()

        session['consortium'] = f'CONTEXT_{consortium}'
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


        """
        Authenticate to Globus via the login route.
        If login is successful, Globus will redirect to the edit page.
        """
        #Indicate the workflow (edit, export, doi) to the Globus auth.
        #session['workflow'] = 'get_uuids'

        # Authenticate to Globus via the login route.
        # If login is successful, Globus will redirect to the get-uuids page.
        return redirect(f'/login')

    # Render the Globus login form.
    return render_template('index.html')