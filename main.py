import os

import firebase_admin
import requests
from dotmap import DotMap
from firebase_admin import auth
from firebase_admin import credentials
from firebase_admin import firestore

# Use the application default credentials
cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(cred, {
    'projectId': "trentiemeciel",
})

ERROR_REPORTING_API_KEY = os.environ["ERROR_REPORTING_API_KEY"]


def from_request(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """

    # Set CORS headers for preflight requests
    if request.method == 'OPTIONS':
        # Allows GET requests from any origin with
        # Authorization header
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'content-type',
            'Access-Control-Max-Age': '3600',
        }
        return '', 204, headers

    from flask import abort
    if request.method != 'POST':
        return abort(405)

    request_data = DotMap(request.get_json())
    access_token = request_data.access_token
    firebase_token = convert_auth0_token_to_firebase_token(access_token)
    headers = {
        'Access-Control-Allow-Origin': '*',
    }
    return ({
                "firebase_token": firebase_token,
                "error_reporting_api_key": ERROR_REPORTING_API_KEY,
            }, 200, headers)


def convert_auth0_token_to_firebase_token(auth0_token):
    # valid auth0_token and get user_profile
    up = get_user_profile(auth0_token)
    upset_user_profile_in_firestore(up)
    return create_firebase_token(up)


def upset_user_profile_in_firestore(user_profile):
    assert user_profile.sub is not None
    sub = user_profile.sub

    db = firestore.client()
    user_doc_ref = db.collection("pax").document(sub)
    user_doc_ref.set(user_profile.toDict(), merge=True)


def create_firebase_token(user_profile):
    uid = user_profile.sub
    custom_token = auth.create_custom_token(uid)
    return str(custom_token, "utf-8")


def get_user_profile(token):
    headers = {
        "Authorization": f"Bearer {token}"
    }

    req = requests.get("https://paxid.eu.auth0.com/userinfo", headers=headers)
    req.raise_for_status()
    resp = req.json()
    return DotMap(resp)
