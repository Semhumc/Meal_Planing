import os
import requests
import json
from .ai_service import generate_meal_suggestions, get_fallback_data

def generate_meal_suggestions(preferences):
    """
    Google AI API kullanarak yemek önerileri oluşturur
    """
    api_key = os.getenv("API_KEY")
    
    print(f"API Key exists: {bool(api_key)}")
    print(f"Preferences received: {preferences}")
    
    if not api_key:
        print("No API key found, using fallback data")
        return get_fallback_data()
    
    # Tercihleri string'e çevir
    cuisine_map = {
        'turkish': 'Türk Mutfağı',
        'italian': 'İtalyan Mutfağı', 
        'asian': 'Asya Mutfağı',
        'mediterranean': 'Akdeniz Mutfağı'
    }
    
    cuisine_name = cuisine_map.get(preferences.get('cuisine', 'turkish'), 'Türk Mutfağı')
    
    prompt = f"""
Kullanıcı tercihleri:
- Kalori hedefi: {preferences.get('calories', 2000)} kcal
- Mutfak tercihi: {cuisine_name}
- Alerjiler: {preferences.get('allergies', 'Yok')}
- Sevdiği yemekler: {preferences.get('favorites', 'Belirtilmedi')}
- Canının çektiği: {preferences.get('cravings', 'Belirtilmedi')}
- Ek notlar: {preferences.get('notes', 'Yok')}

Bu tercihlere göre {cuisine_name} yemekleri öner. SADECE JSON formatında cevap ver.
"""

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/text-bison-001:generateContent?key={api_key}"
        
        headers = {
            'Content-Type': 'application/json',
        }
        
        data = {
            "prompt": prompt,
            "temperature": 0.7,
            "maxOutputTokens": 2000
        }
        
        print("Making API request to Google AI...")
        response = requests.post(url, headers=headers, json=data, timeout=30)
        print(f"API Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("API call successful")
            
            # Response parsing (v1beta format)
            if "candidates" in result and len(result["candidates"]) > 0:
                content = result["candidates"][0]["content"]
                
                # Eğer content string ise parse et
                try:
                    parsed_data = json.loads(content)
                    print("Successfully parsed AI response")
                    return parsed_data
                except json.JSONDecodeError as e:
                    print(f"JSON parse error: {e}")
                    return get_fallback_data()
            else:
                print("No candidates in API response")
                return get_fallback_data()
        else:
            print(f"Google AI API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return get_fallback_data()
            
    except requests.exceptions.Timeout:
        print("API request timeout")
        return get_fallback_data()
    except Exception as e:
        print(f"AI Service Error: {e}")
        return get_fallback_data()



def generate_shopping_list(selected_meals):
    ingredients_set = set()
    for meal in selected_meals:
        for ing in meal.get("ingredients", []):
            ingredients_set.add(ing)
    return list(ingredients_set)

def get_fallback_data():
    """Hata durumunda kullanılacak varsayılan data"""
    print("Using fallback data")
    return {
        "starter": [
            {"id": 1, "name": "Mercimek Çorbası", "calories": 180, "ingredients": ["kırmızı mercimek", "soğan", "havuç", "tereyağı", "un"], "description": "Geleneksel Türk çorbası"},
            {"id": 2, "name": "Ezogelin Çorbası", "calories": 160, "ingredients": ["kırmızı mercimek", "bulgur", "domates salçası", "soğan"], "description": "Antep yöresine özgü çorba"}
        ],
        "main": [
            {"id": 3, "name": "Tavuk Şiş", "calories": 320, "ingredients": ["tavuk göğsü", "soğan", "biber", "zeytinyağı", "baharat"], "description": "Mangalda pişirilmiş tavuk şiş"},
            {"id": 4, "name": "Karnıyarık", "calories": 280, "ingredients": ["patlıcan", "kıyma", "soğan", "domates", "biber"], "description": "Fırında pişirilmiş geleneksel yemek"}
        ],
        "side": [
            {"id": 5, "name": "Pilav", "calories": 220, "ingredients": ["pirinç", "tereyağı", "tuz", "su"], "description": "Klasik Türk pilavı"},
            {"id": 6, "name": "Çoban Salata", "calories": 80, "ingredients": ["domates", "salatalık", "soğan", "maydanoz", "zeytinyağı"], "description": "Taze sebze salatası"}
        ],
        "dessert": [
            {"id": 7, "name": "Sütlaç", "calories": 200, "ingredients": ["süt", "pirinç", "şeker", "tarçın"], "description": "Geleneksel Türk tatlısı"},
            {"id": 8, "name": "Kazandibi", "calories": 250, "ingredients": ["süt", "şeker", "mısır nişastası", "vanilya"], "description": "Osmanlı saray tatlısı"}
        ]
    }
