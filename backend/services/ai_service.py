import os
import openai

openai.api_key = os.getenv("API_KEY")

def generate_meal_suggestions(preferences):
    prompt = f"""
    Kullanıcı şu tercihleri girdi:
    Kalori: {preferences.get('calories')}
    Mutfak: {preferences.get('cuisine')}
    Alerjiler: {preferences.get('allergies')}
    Favoriler: {preferences.get('favorites')}
    Canı çektiği: {preferences.get('cravings')}
    Notlar: {preferences.get('notes')}

    Bu tercihlere göre 2 başlangıç, 2 ana yemek, 1 yan yemek, 1 tatlı öner.
    JSON formatında döndür: {{ "starter": [...], "main": [...], "side": [...], "dessert": [...] }}
    """

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",  # veya Gemini API
        messages=[{"role": "system", "content": "Sen yemek öneri asistanısın."},
                  {"role": "user", "content": prompt}],
        temperature=0.7
    )

    return response.choices[0].message["content"]
