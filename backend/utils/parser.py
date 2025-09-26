import json

def parse_ai_response(ai_response: str):
    """
    AI'den dönen JSON stringini parse eder.
    Eğer JSON değilse boş dict döner.
    """
    try:
        data = json.loads(ai_response)
        if not isinstance(data, dict):
            return {}
        return data
    except json.JSONDecodeError:
        return {}


def extract_ingredients(meal_plan: dict):
    """
    Meal plan içindeki tüm malzemeleri tek bir listede toplar.
    Örn:
    {
      "starter": [{"name": "Çorba", "ingredients": ["su", "mercimek"]}],
      "main": [...]
    }
    => ["su", "mercimek", ...]
    """
    ingredients = set()
    for meals in meal_plan.values():
        for meal in meals:
            for ing in meal.get("ingredients", []):
                ingredients.add(ing.lower())
    return list(ingredients)
