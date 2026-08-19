"""
Index route that:
1. obtains Globus environment and donor id from a WTForm (GlobusForm)
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
        consortium = request.form.get('consortium')
        datasetid = request.form.get('datasetid')
        # Get the consortium from the request.
        if consortium.upper() not in ['HUBMAP', 'SENNET']:
            return make_response(f'Invalid consortium: {consortium}', 400)
        consortium = consortium.upper()

        session['consortium'] = f'CONTEXT_{consortium}'
        session['datasetid'] = datasetid

        """
        Authenticate to Globus via the login route.
        If login is successful, Globus will redirect to the edit page.
        """
        #Indicate the workflow (edit, export, doi) to the Globus auth.
        session['workflow'] = 'get_uuids'

        # Authenticate to Globus via the login route.
        # If login is successful, Globus will redirect to the get-uuids page.
        return redirect(f'/login')

    # Render the Globus login form.
    return render_template('index.html')