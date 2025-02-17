from flask import Blueprint, Response, Request, jsonify, request

api = Blueprint('api', __name__)

@api.route('/detect_hand', methods=['POST'])
def hand_stimation():
    data = request.get_json()
    return jsonify(data)
