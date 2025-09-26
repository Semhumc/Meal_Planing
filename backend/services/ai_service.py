import os
import requests
import json

def generate_meal_suggestions(preferences):
    api_key = os.getenv("API_KEY")
    print(f"API Key exists: {bool(api_key)}")
    print(f"Preferences received: {preferences}")

    if not api_key:
        return get_fallback_data()

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
        headers = {'Content-Type': 'application/json'}
        {
  "input": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "Senin prompt metnin burada olacak"
        }
      ]
    }
  ],
  "temperature": 0.7,
  "candidate_count": 1,
  "top_p": 0.95,
  "top_k": 40
}

}

        print("Making API request to Google AI...")
        response = requests.post(url, headers=headers, json=data, timeout=30)
        print(f"API Response status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            if "candidates" in result and len(result["candidates"]) > 0:
                content = result["candidates"][0].get("content")
                try:
                    parsed_data = json.loads(content)
                    return parsed_data
                except Exception as e:
                    print(f"JSON parse error: {e}")
                    return get_fallback_data()
            else:
                return get_fallback_data()
        else:
            print(f"Google AI API Error: {response.status_code} {response.text}")
            return get_fallback_data()
    except Exception as e:
        print(f"AI Service Error: {e}")
        return get_fallback_data()

def get_fallback_data():
    return {
        "starter": [
            {"id": 1, "name": "Mercimek Çorbası", "calories": 180, "ingredients": ["kırmızı mercimek", "soğan", "havuç"], "description": "Geleneksel Türk çorbası"}
        ],
        "main": [
            {"id": 2, "name": "Tavuk Şiş", "calories": 320, "ingredients": ["tavuk göğsü", "soğan", "biber"], "description": "Mangalda pişirilmiş tavuk"}
        ],
        "side": [
            {"id": 3, "name": "Pilav", "calories": 220, "ingredients": ["pirinç", "tereyağı"], "description": "Klasik Türk pilavı"}
        ],
        "dessert": [
            {"id": 4, "name": "Sütlaç", "calories": 200, "ingredients": ["süt", "pirinç", "şeker"], "description": "Geleneksel Türk tatlısı"}
        ]
    }
