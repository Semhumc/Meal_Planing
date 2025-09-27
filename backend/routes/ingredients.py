from flask import Blueprint, request, jsonify
import json
from services.recipe_service import generate_shopping_list

ingredients_bp = Blueprint("ingredients", __name__)

@ingredients_bp.route('/missing', methods=['POST'])
def get_missing_ingredients():
    data = request.get_json()
    ai_response = data.get("ai_response", {})
    pantry = data.get("pantry", [])

    # Eğer string geliyorsa JSON'a çevir
    if isinstance(ai_response, str):
        try:
            ai_response = json.loads(ai_response)
        except Exception:
            return jsonify({"error": "ai_response is not valid JSON"}), 400

    result = generate_shopping_list(ai_response, pantry)
    return jsonify({"missing_ingredients": result})
