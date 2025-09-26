from flask import Flask
from flask_cors import CORS
from config import Config
from routes.ingredients import ingredients_bp
from routes.meals import meals_bp

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
