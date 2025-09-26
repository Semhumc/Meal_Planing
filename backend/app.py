from flask import Flask
from config import Config
from routes.ingredients import ingredients_bp

app = Flask(__name__)
app.config.from_object(Config)

# Blueprint ekleme
app.register_blueprint(ingredients_bp, url_prefix="/api/ingredients")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
