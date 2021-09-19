import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

import traceback

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
# db_drop_and_create_all()

# ROUTES

@app.route('/drinks')
def get_drinks():
    try:
        drinks = Drink.query.all()
        drinks_short = [drink.short() for drink in drinks]
        return jsonify({
            "success": True,
            "drinks": drinks_short
        }), 200
    except:
        traceback.print_exc()
        abort(500)

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth(permission='get:drinks-detail')
def get_drinks_detail(payload):
    try:
        drinks = Drink.query.all()
        for drink in drinks:
            print("drink long", drink.long())
        drinks_short = [drink.long() for drink in drinks]
        return jsonify({
            "success": True,
            "drinks": drinks_short
        }), 200
    except:
        traceback.print_exc()
        abort(500)



@app.route('/drinks', methods=['POST'])
@requires_auth(permission='post:drinks')
def create_drink(payload):
    body = request.get_json()
    title = body['title']
    recipe = json.dumps(body['recipe'])

    drink = Drink(title=title, recipe=recipe)
    drink.insert()
    return jsonify({
        "success": True,
        "drinks": [drink.long()]
    }), 201




@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth(permission='patch:drinks')
def update_drink(payload, id):
    drink = Drink.query.get(id)
    if drink is None:
        abort(404)
    try:
        body = request.get_json()
        title = body.get('title')
        recipe = body.get('recipe')
        if title:
            drink.title = title
        if  recipe:
            drink.recipe = json.dumps(recipe)
        drink.update()
        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        }), 200
    except:
        traceback.print_exc()
        abort(500)




@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth(permission='delete:drinks')
def delete_drink(payload, id):
    drink = Drink.query.get(id)
    if drink is None:
        abort(404)
    try:
        drink.delete()
        return jsonify({
            "success": True,
            "delete": id
        }), 200
    except:
        traceback.print_exc()
        abort(500)


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def handle_unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def handle_not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

@app.errorhandler(500)
def handle_server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "Internal Server Error. Check the server logs to see what happend"
    }), 500

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def handle_auth_errors(exception):
    return jsonify(exception.error), exception.status_code