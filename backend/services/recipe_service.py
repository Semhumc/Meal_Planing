import json

# Örnek veri: Kullanıcının evdeki mevcut malzemeleri
# (Sen bunu DB'den ya da frontend'den alabilirsin)
USER_PANTRY = ["yumurta", "süt", "un", "domates", "peynir"]

def parse_meal_suggestions(ai_response: str):
    """
    AI'den dönen JSON stringini alır ve Python objesine çevirir.
    Beklenen format:
    {
      "starter": [{"name": "Çorba", "ingredients": ["su", "mercimek", "soğan"]}],
      "main": [{"name": "Köfte", "ingredients": ["kıyma", "soğan", "yumurta"]}],
      ...
    }
    """
    try:
        return json.loads(ai_response)
    except json.JSONDecodeError:
        return {}


def get_missing_ingredients(meal_plan, pantry=None):
    """
    Tariflerde geçen tüm malzemeleri tarar,
    kullanıcının dolabında olmayanları döner.
    """
    if pantry is None:
        pantry = USER_PANTRY

    missing = set()

    for category, meals in meal_plan.items():
        for meal in meals:
            for ingredient in meal.get("ingredients", []):
                if ingredient.lower() not in [p.lower() for p in pantry]:
                    missing.add(ingredient.lower())

    return list(missing)


def generate_shopping_list(ai_response: str, pantry=None):
    """
    AI cevabını parse eder, eksik malzemeleri çıkarır
    ve alışveriş listesi döner.
    """
    meal_plan = parse_meal_suggestions(ai_response)
    missing_items = get_missing_ingredients(meal_plan, pantry)
    return {
        "meal_plan": meal_plan,
        "missing_ingredients": missing_items
    }
