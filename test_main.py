import dotenv
import pytest
from box import Box
from core import firestore_client
from google.api_core.exceptions import NotFound
from google.cloud.firestore_v1 import CollectionReference, DocumentReference, Client
from mockito import mock


@pytest.fixture(autouse=True)
def env():
    dotenv.load_dotenv()


@pytest.fixture()
def user_profile_json():
    return {
        'sub': 'auth0|5ff8a6010402c500756514ba', 'nickname': 'admin', 'name': 'admin@30emeciel.fr', 'picture': 'https://s.gravatar.com/avatar/448e7b02f9759bca54e864205d858e34?s=480&r=pg&d=https%3A%2F%2Fcdn.auth0.com%2Favatars%2Fad.png', 'updated_at': '2021-04-29T19:14:55.523Z', 'email': 'admin@30emeciel.fr', 'email_verified': True
    }


@pytest.fixture()
def user_profile(user_profile_json):
    return Box(user_profile_json)


@pytest.fixture()
def db(when):
    ret = mock(Client)
    when(firestore_client).db().thenReturn(ret)
    return ret


def test_upset_user_profile_in_firestore(when, db, user_profile):
    collection = mock(CollectionReference)
    document = mock(DocumentReference)
    when(db).collection("pax").thenReturn(collection)
    when(collection).document(user_profile.sub).thenReturn(document)
    when(document).update(...).thenReturn()
    import main
    main.upset_user_profile_in_firestore(user_profile)


def test_upset_user_profile_in_firestore_not_existant(when, db):
    not_existant_up = Box({
        "sub": "non_existent"
    })
    collection = mock(CollectionReference)
    document = mock(DocumentReference)
    when(db).collection("pax").thenReturn(collection)
    when(collection).document("non_existent").thenReturn(document)
    when(document).update(...).thenRaise(NotFound("not found"))
    when(document).set(...).thenReturn()
    import main
    main.upset_user_profile_in_firestore(not_existant_up)


def test_get_user_profile(when, user_profile_json):
    import main
    import requests
    response = mock({'status_code': 200, 'json': lambda: user_profile_json})
    when(requests).get("https://paxid.eu.auth0.com/userinfo", ...).thenReturn(response)
    main.get_user_profile("dummy_token")
