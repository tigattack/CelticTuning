"""Query Celtic Tuning from a simplified web interfaced"""
import os

from flask import Flask, render_template, request
from flask.wrappers import Response

from Celtic import Celtic

template_dir = os.path.abspath('./web_templates')
app = Flask(__name__, template_folder=template_dir)

def respond_error(error_text: str):
    """Just a silly little wrapper for a wrapper (flask Response)"""
    return Response(
        error_text,
        status=400,
    )

def vehicle_info(vrn: str):
    """Just a silly little wrapper for my Celtic class"""
    try:
        celtic = Celtic(vrn)
    except ValueError as err:
        return respond_error(str(err))

    return celtic.get_all()

@app.route('/')
def index():
    """
    Function for web interface.
    'Interface' is a bit of a stretch but just go with it.
    """
    return render_template('page.html')


@app.route('/get_vehicle', methods=['GET', 'POST'])
def api_responder():
    """
    Function for API requests
    Example: GET app/get_vehicle?vrn=ab12cde
    """

    def empty_vrn_error():
        return respond_error('ERROR: vrn parameter missing or empty.')

    if request.method == 'GET':
        if not request.args.get('vrn'):
            return empty_vrn_error()

        vrn = request.args.get('vrn', '')
        if len(vrn) == 0:
            return empty_vrn_error()

    elif request.method == 'POST':
        if not request.form.get('vrn'):
            return empty_vrn_error()

        vrn = request.form.get('vrn', '')
        if len(vrn) == 0:
            return empty_vrn_error()

    return vehicle_info(vrn)

if __name__ == "__main__":
    app.run()
