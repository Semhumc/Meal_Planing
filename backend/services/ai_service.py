import os
import requests
import json
import re

def clean_json_response(content):
    """AI'dan gelen response'u temizle ve JSON'a çevir"""
    try:
        # 1. Markdown code blocks'larını kaldır
        content = content.strip()
        if content.startswith('```json'):
            content = content[7:]
        elif content.startswith('```'):
            content = content[3:]
        
        if content.endswith('```'):
            content = content[:-3]
        
        content = content.strip()
        
        # 2. İlk { ile son } arasındaki kısmı al
        start_idx = content.find('{')
        end_idx = content.rfind('}')
        
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            content = content[start_idx:end_idx+1]
        
        # 3. Yaygın JSON hatalarını düzelt
        # Trailing comma'ları kaldır
        content = re.sub(r',(\s*[}\]])', r'\1', content)
        
        # Çift virgülleri düzelt
        content = re.sub(r',,+', ',', content)
        
        # 4. JSON parse et
        return json.loads(content)
        
    except json.JSONDecodeError as e:
        print(f"JSON parse error after cleaning: {e}")
        print(f"Cleaned content: {content[:500]}...")
        
        # 5. Manuel parsing - daha basit yaklaşım
        try:
            # Regex ile temel yapıyı çıkar
            return extract_meals_from_text(content)
        except Exception as manual_error:
            print(f"Manuel parsing also failed: {manual_error}")
            return None
    except Exception as e:
        print(f"Error in clean_json_response: {e}")
        return None

def extract_meals_from_text(text):
    """Text'ten yemek bilgilerini regex ile çıkar"""
    result = {
        "starter": [],
        "main": [],
        "side": [],
        "dessert": []
    }
    
    # Her kategori için pattern'lar
    categories = ["starter", "main", "side", "dessert"]
    
    for category in categories:
        # Bu kategorideki yemekleri bul
        pattern = rf'"{category}":\s*\[(.*?)\]'
        match = re.search(pattern, text, re.DOTALL)
        
        if match:
            items_text = match.group(1)
            # Her item'ı parse et
            items = parse_meal_items(items_text, category)
            result[category] = items
    
    return result

def parse_meal_items(items_text, category):
    """Yemek item'larını parse et"""
    items = []
    
    # Basit item pattern'ı
    item_pattern = r'\{[^{}]*\}'
    matches = re.findall(item_pattern, items_text)
    
    id_counter = 1 if category == "starter" else (3 if category == "main" else (5 if category == "side" else 7))
    
    for match in matches:
        try:
            # Name'i bul
            name_match = re.search(r'"name":\s*"([^"]*)"', match)
            name = name_match.group(1) if name_match else f"{category.capitalize()} Yemeği"
            
            # Calories'i bul
            cal_match = re.search(r'"calories":\s*(\d+)', match)
            calories = int(cal_match.group(1)) if cal_match else 200
            
            # Ingredients'i bul
            ing_match = re.search(r'"ingredients":\s*\[(.*?)\]', match)
            ingredients = []
            if ing_match:
                ing_text = ing_match.group(1)
                ing_items = re.findall(r'"([^"]*)"', ing_text)
                ingredients = ing_items[:5]  # Max 5 ingredient
            
            if not ingredients:
                ingredients = ["malzeme1", "malzeme2", "malzeme3"]
            
            # Description'ı bul
            desc_match = re.search(r'"description":\s*"([^"]*)"', match)
            description = desc_match.group(1) if desc_match else f"Lezzetli {name.lower()}"
            
            items.append({
                "id": id_counter,
                "name": name,
                "calories": calories,
                "ingredients": ingredients,
                "description": description
            })
            
            id_counter += 1
            
        except Exception as e:
            print(f"Error parsing item: {e}")
            continue
    
    return items

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
    
    # Çok daha basit ve kısa prompt
    prompt = f"""Sadece JSON döndür:

{{
    "starter": [{{"id": 1, "name": "Çorba", "calories": 180, "ingredients": ["malzeme1", "malzeme2"], "description": "açıklama"}}],
    "main": [{{"id": 3, "name": "Ana Yemek", "calories": 350, "ingredients": ["malzeme3", "malzeme4"], "description": "açıklama"}}],
    "side": [{{"id": 5, "name": "Yan Yemek", "calories": 150, "ingredients": ["malzeme5"], "description": "açıklama"}}],
    "dessert": [{{"id": 7, "name": "Tatlı", "calories": 250, "ingredients": ["malzeme6"], "description": "açıklama"}}]
}}

Mutfak: {cuisine_name}, Kalori: {preferences.get('calories', 2000)}, Alerji: {preferences.get('allergies', 'yok')}"""

    # Denenmesi gereken modeller - güncel sıralama
    models = [
        
        "gemini-2.5-flash"
    ]

    for model in models:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            
            headers = {
                'Content-Type': 'application/json',
            }
            
            data = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": prompt
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.3,
                    "maxOutputTokens": 8192,  # Maksimum token artırıldı
                    "topP": 0.8,
                    "topK": 40
                }
            }
            
            print(f"Trying model: {model}")
            response = requests.post(url, headers=headers, json=data, timeout=30)
            print(f"API Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"Success with model: {model}")
                print(f"Full API response structure: {json.dumps(result, indent=2)[:500]}...")
                
                # Farklı response yapılarını handle et
                content = None
                
                print(f"Finish reason: {result['candidates'][0].get('finishReason', 'unknown')}")
                
                # Standard Gemini response
                if 'candidates' in result and len(result['candidates']) > 0:
                    candidate = result['candidates'][0]
                    print(f"Candidate structure: {json.dumps(candidate, indent=2)[:300]}...")
                    
                    # Gemini 2.5 format kontrolü
                    if 'content' in candidate:
                        content_obj = candidate['content']
                        
                        # Parts array varsa
                        if 'parts' in content_obj and len(content_obj['parts']) > 0:
                            for part in content_obj['parts']:
                                if 'text' in part:
                                    content = part['text']
                                    break
                        # Direct text varsa
                        elif 'text' in content_obj:
                            content = content_obj['text']
                    # Direkt text field'ı varsa
                    elif 'text' in candidate:
                        content = candidate['text']
                    elif 'output' in candidate:
                        content = candidate['output']
                
                # Direct response (bazı API versiyonları)
                elif 'text' in result:
                    content = result['text']
                elif 'output' in result:
                    content = result['output']
                
                # Eğer response kesilmişse ve content yoksa, akıllı fallback kullan
                if not content and result['candidates'][0].get('finishReason') == 'MAX_TOKENS':
                    print("Response was cut due to MAX_TOKENS, using intelligent fallback")
                    return generate_smart_fallback_data(preferences)
                
                if content:
                    print(f"Extracted content: {content[:300]}...")
                    
                    # Geliştirilmiş JSON temizleme
                    parsed_data = clean_json_response(content)
                    
                    if parsed_data and validate_meal_structure(parsed_data):
                        print("Successfully parsed and validated AI response")
                        return parsed_data
                    else:
                        print("Failed to parse or validate response, trying next model")
                        continue
                else:
                    print(f"Could not extract content from response for model: {model}")
                    print(f"Available keys: {list(result.keys())}")
                    continue
            else:
                print(f"Model {model} failed: {response.status_code}")
                print(f"Response: {response.text}")
                continue
                
        except requests.exceptions.Timeout:
            print(f"Timeout for model: {model}")
            continue
        except Exception as e:
            print(f"Error with model {model}: {e}")
            continue

    # Hiçbir model çalışmazsa fallback
    print("All models failed, using fallback data")
    return get_fallback_data()

def validate_meal_structure(data):
    """Meal data'nın yapısını kontrol et"""
    if not isinstance(data, dict):
        return False
    
    required_categories = ['starter', 'main', 'side', 'dessert']
    for category in required_categories:
        if category not in data or not isinstance(data[category], list):
            return False
        
        for meal in data[category]:
            if not isinstance(meal, dict):
                return False
            if not all(key in meal for key in ['id', 'name', 'calories', 'ingredients', 'description']):
                return False
            if not isinstance(meal['ingredients'], list):
                return False
    
    return True

def generate_smart_fallback_data(preferences):
    """Kullanıcı tercihlerine göre akıllı fallback data üret"""
    
    cuisine = preferences.get('cuisine', 'turkish')
    calories = preferences.get('calories', 2000)
    allergies = preferences.get('allergies', '').lower()
    favorites = preferences.get('favorites', '').lower()
    cravings = preferences.get('cravings', '').lower()
    
    print(f"Using smart fallback for {cuisine} cuisine")
    
    # Basit mutfak seçimi
    if cuisine == 'asian':
        return {
            "starter": [
                {"id": 1, "name": "Tom Yum Çorbası", "calories": 200, "ingredients": ["karides", "limon otu", "chili"], "description": "Acılı Thai çorbası"},
                {"id": 2, "name": "Miso Çorbası", "calories": 150, "ingredients": ["miso", "tofu", "wakame"], "description": "Japon çorbası"}
            ],
            "main": [
                {"id": 3, "name": "Pad Thai", "calories": 400, "ingredients": ["rice noodle", "karides", "yumurta"], "description": "Thai noodle"},
                {"id": 4, "name": "Kung Pao Tavuk", "calories": 350, "ingredients": ["tavuk", "fıstık", "biber"], "description": "Acılı Çin yemeği"}
            ],
            "side": [
                {"id": 5, "name": "Fried Rice", "calories": 250, "ingredients": ["pirinç", "yumurta", "sebze"], "description": "Kızarmış pirinç"}
            ],
            "dessert": [
                {"id": 6, "name": "Mango Sticky Rice", "calories": 220, "ingredients": ["mango", "glutinous rice"], "description": "Thai tatlısı"}
            ]
        }
    elif cuisine == 'italian':
        return {
            "starter": [
                {"id": 1, "name": "Bruschetta", "calories": 180, "ingredients": ["ekmek", "domates", "fesleğen"], "description": "İtalyan aperatifi"},
                {"id": 2, "name": "Minestrone", "calories": 160, "ingredients": ["sebze", "fasulye"], "description": "İtalyan sebze çorbası"}
            ],
            "main": [
                {"id": 3, "name": "Spaghetti Carbonara", "calories": 450, "ingredients": ["spagetti", "yumurta", "parmesan"], "description": "Klasik pasta"},
                {"id": 4, "name": "Margherita Pizza", "calories": 380, "ingredients": ["hamur", "domates", "mozzarella"], "description": "Geleneksel pizza"}
            ],
            "side": [
                {"id": 5, "name": "Caesar Salad", "calories": 200, "ingredients": ["marul", "parmesan", "kruton"], "description": "İtalyan salatası"}
            ],
            "dessert": [
                {"id": 6, "name": "Tiramisu", "calories": 300, "ingredients": ["mascarpone", "kahve"], "description": "İtalyan tatlısı"}
            ]
        }
    else:  # Turkish (default)
        return {
            "starter": [
                {"id": 1, "name": "Mercimek Çorbası", "calories": 180, "ingredients": ["kırmızı mercimek", "soğan", "havuç"], "description": "Geleneksel Türk çorbası"},
                {"id": 2, "name": "Ezogelin Çorbası", "calories": 160, "ingredients": ["mercimek", "bulgur", "salça"], "description": "Antep çorbası"}
            ],
            "main": [
                {"id": 3, "name": "Köfte", "calories": 350, "ingredients": ["kıyma", "soğan", "ekmek içi"], "description": "Türk köftesi"},
                {"id": 4, "name": "Tavuk Şiş", "calories": 320, "ingredients": ["tavuk", "biber", "soğan"], "description": "Izgara tavuk"}
            ],
            "side": [
                {"id": 5, "name": "Pilav", "calories": 220, "ingredients": ["pirinç", "tereyağı"], "description": "Türk pilavı"}
            ],
            "dessert": [
                {"id": 6, "name": "Sütlaç", "calories": 200, "ingredients": ["süt", "pirinç", "şeker"], "description": "Türk tatlısı"}
            ]
        }

def get_fallback_data():
    """Hata durumunda kullanılacak varsayılan data"""
    print("Using basic fallback data")
    return generate_smart_fallback_data({'cuisine': 'turkish', 'calories': 2000})

def test_api_key():
    """API key'i test et"""
    api_key = os.getenv("API_KEY")
    if not api_key:
        return False, "No API key found"
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            models = response.json().get('models', [])
            model_names = [model.get('name', '') for model in models]
            return True, f"Available models: {model_names}"
        else:
            return False, f"API Error: {response.status_code} - {response.text}"
    except Exception as e:
        return False, f"Connection Error: {e}"