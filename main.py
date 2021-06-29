import os

import requests
from box import Box
from core import firestore_client
from firebase_admin import auth
from google.api_core.exceptions import NotFound
from google.cloud.firestore_v1 import SERVER_TIMESTAMP

ERROR_REPORTING_API_KEY = os.environ["ERROR_REPORTING_API_KEY"]

db = firestore_client.db()


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

    request_data = Box(request.get_json())
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
    assert up.sub is not None
    pax_id = up.pop("sub")
    upset_user_profile_in_firestore(pax_id, up)
    return create_firebase_token(pax_id)


def upset_user_profile_in_firestore(pax_id, user_profile):
    user_profile_dict = user_profile.to_dict()
    user_doc_ref = db.collection("pax").document(pax_id)
    try:
        user_doc_ref.update(user_profile_dict)
    except NotFound:
        user_profile_dict.update({
            "created": SERVER_TIMESTAMP,
            "state": "AUTHENTICATED",
        })
        user_doc_ref.set(user_profile_dict, merge=True)


def create_firebase_token(pax_id):
    custom_token = auth.create_custom_token(pax_id)
    return str(custom_token, "utf-8")


def get_user_profile(token):
    headers = {
        "Authorization": f"Bearer {token}"
    }

    req = requests.get("https://paxid.eu.auth0.com/userinfo", headers=headers)
    req.raise_for_status()
    resp = req.json()
    obj = Box(resp)
    if "email" in obj and obj.name == obj.email:  # auth0 weird name
        obj.name = obj.get("nickname") or obj.email
    return obj
