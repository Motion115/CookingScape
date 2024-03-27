import jwt
import time
import json

def getToken(API_key_json):
    API_key = enable_API(API_key_json)
    token = generate_token(API_key, 3600)
    return token


def enable_API(API_key_json):
    # read json
    with open(API_key_json, 'r') as f:
        API_key = json.load(f)["zhipu_api"]
    return API_key

def generate_token(apikey: str, exp_seconds: int):
    try:
        id, secret = apikey.split(".")
    except Exception as e:
        raise Exception("invalid apikey", e)
 
    payload = {
        "api_key": id,
        "exp": int(round(time.time() * 1000)) + exp_seconds * 1000,
        "timestamp": int(round(time.time() * 1000)),
    }
 
    return jwt.encode(
        payload,
        secret,
        algorithm="HS256",
        headers={"alg": "HS256", "sign_type": "SIGN"},
    )