from flask import Blueprint, request, jsonify
from services.recipe_service import generate_shopping_list

ingredients_bp = Blueprint("ingredients", __name__)

@ingredients_bp.route("/missing", methods=["POST"])
def get_missing_ingredients():
    """
    Request body:
    {
      "ai_response": "...",   # AI'den dönen JSON string
      "pantry": ["yumurta", "un", "süt"]   # Kullanıcının evdeki malzemeleri
    }

    Response:
    {
      "meal_plan": {...},             # Tariflerin tamamı
      "missing_ingredients": [...]    # Eksik malzemeler
    }
    """
    data = request.get_json()

    if not data or "ai_response" not in data:
        return jsonify({"error": "ai_response is required"}), 400

    ai_response = data["ai_response"]
    pantry = data.get("pantry", [])

    result = generate_shopping_list(ai_response, pantry)

    return jsonify(result), 200
