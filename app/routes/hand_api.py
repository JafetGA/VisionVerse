from flask import Blueprint, Response, Request, jsonify, request
import cv2, base64
import numpy as np
from app.services.hand_detection import HandDetector

api = Blueprint('api', __name__)

@api.route('/detect_hand', methods=['POST'])
def hand_stimation():
    data = request.get_json()
    frame_str = data['frame'].split(',')[1]
    decoded_img = base64.b64decode(frame_str)
    np_arr = np.frombuffer(decoded_img, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    detector = HandDetector()
    results = detector.find_hands(img)
    return jsonify({"coordinates": results["coordinates"]})
