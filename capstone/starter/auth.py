import json
from flask import request, _request_ctx_stack, abort
from functools import wraps
from jose import jwt
from urllib.request import urlopen
from dotenv import load_dotenv, dotenv_values
from os import environ as env

# load environment variables from .env file
load_dotenv(override=True)

AUTH0_DOMAIN = env['AUTH0_DOMAIN']
ALGORITHMS = [env['ALGORITHMS']]
API_AUDIENCE = env['API_AUDIENCE']


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


def get_token_auth_header():
    auth = request.headers.get("Authorization", None)

    # check if an "Authorization" header is included
    if not auth:
        raise AuthError(
        {
        "code": "authorization_header_missing",
        "description": "Authorization header expected"
        },
        401)
    
    # split into "bearer" and token (they are a space apart)
    parts = auth.split(' ')

    # check that it is a Bearer authorization token
    if parts[0].lower() != "bearer":
        raise AuthError(
            {
            "code": "invalid_header",
            "description": "Authorization of type Bearer expected"
            },
            401)

    # check that a token is included
    if len(parts) == 1:
        raise AuthError(
            {
            "code": "invalid_header",
            "description": "Token is expected in header"
            },
            401)

    # check that no more than the token is included
    if len(parts) > 2:
        raise AuthError(
            {
            "code": "invalid_header",
            "description": "Bearer token expected"
            })

    token = parts[1]
    return token

def check_permissions(permission, payload):
    if "permissions" not in payload:
        raise AuthError(
            {
            "code": "permissions_missing",
            "description": "Permissions expected in payload"
            }, 400)

    if permission not in payload["permissions"]:
        raise AuthError(
            {
            "code": "action_not_allowed",
            "description": "Permission missing for action"
            }, 403)

    return True


def verify_decode_jwt(token):
    # get the header from the token that was passed. could be correct JWT
    # that was made with a private key from Auth0, or could be false
    unverified_header = jwt.get_unverified_header(token)
    #print(unverified_header)

    # check that a kid is included in the unverified_header
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)

    # verify the token
    # get the JSON url for the jwt
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')

    # get the public JSON web key to verify the signature
    jwkids = json.loads(jsonurl.read())

    # match kids from private and public keys
    rsa_key = {}
    for key in jwkids['keys']:
        #print(key['kid'])
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
                }

    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )
            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, check the audience and issuer.'
            }, 401)
        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)

    raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to find the appropriate key.'
            }, 400)

def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            try:
                payload = verify_decode_jwt(token)
            except:
                abort(401)

            check_permissions(permission, payload)

            return f(*args, **kwargs)
        return wrapper
    return requires_auth_decorator