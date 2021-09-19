import json
from flask import request, _request_ctx_stack
from functools import wraps
from jose import jwt
from urllib.request import urlopen


def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            f(*args, **kwargs)
        return wrapper
    return requires_auth_decorator

AUTH0_DOMAIN = 'mhassan.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'coffee-shop'

## AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


## Auth Header

def get_token_auth_header():
    auth_header = request.headers.get('Authorization', None)
    if not auth_header:
        raise AuthError({
            "code": "missing_header",
            "description": "No authorization header found"
        }, 401)

    header_parts = auth_header.split(" ")

    if header_parts[0].lower() != "bearer":
        raise AuthError({
            "code": "invalid_header",
            "description": "Auth Header is malformed"
            }, 401)

    return header_parts[1]


def check_permissions(permission, payload):
    payload_permissions = payload.get('permissions')
    if not payload_permissions:
        raise AuthError({
            "code": "no_permission",
            "description": "No perissions found"
        }, 403)
    if permission not in payload_permissions:
        raise AuthError({
            "code":"no_permission",
            "description": "Not allowed permission"
            }, 403)
    return True



def verify_decode_jwt(token):
    jsonurl = urlopen("https://"+AUTH0_DOMAIN+"/.well-known/jwks.json")
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError({
            "code": "invalid_token_header",
            "description": "token header must have a key id"
        }, 401)
    for key in jwks['keys']:
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
                "code": "expired_token",
                "description": "the provided token is expired"
            }, 401)
        except jwt.JWTClaimsError:
            raise AuthError({
                "code": "invalid_claims",
                "description": "invalid token claims"
            }, 401)
        except Exception:
            raise AuthError({
                "code": "invalid_token_header",
                "description": "unable to verify token"
            }, 401)
    raise AuthError({
        "code": "invalid_token_header",
        "description": "can not find the appropriate key"
    }, 401)



def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator