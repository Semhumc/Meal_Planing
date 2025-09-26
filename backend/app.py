from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from routes.ingredients import ingredients_bp
from routes.meals import meals_bp
from services.ai_service import test_api_key

app = Flask(__name__)
app.config.from_object(Config)

# CORS'u etkinleştir
CORS(app)

# Blueprint'leri ekle
app.register_blueprint(ingredients_bp, url_prefix="/api/ingredients")
app.register_blueprint(meals_bp, url_prefix="/api/meals")

@app.route('/')
def home():
    return {"message": "Smart Grocery API is running!"}

@app.route('/test-api')
def test_api():
    """Google AI API key'ini test et"""
    try:
        success, message = test_api_key()
        return jsonify({
            "api_working": success,
            "message": message
        })
    except Exception as e:
        return jsonify({
            "api_working": False,
            "message": f"Test failed: {str(e)}"
        })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)