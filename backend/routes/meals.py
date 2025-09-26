from flask import Blueprint, request, jsonify
from services.ai_service import generate_meal_suggestions

meals_bp = Blueprint("meals", __name__)

@meals_bp.route("/", methods=["POST"])
def get_meals():
    data = request.get_json()
    preferences = data.get("preferences", {})
    suggestions = generate_meal_suggestions(preferences)
    return jsonify(suggestions)
