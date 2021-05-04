import os

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    import main

    # get the token using postman
    firebase_token = main.convert_auth0_token_to_firebase_token(os.environ["AUTH0_TEST_TOKEN"])
    print(f"firebase_token: {firebase_token}")
