import requests

BASE_URL = 'http://127.0.0.1:8000/api'
def p(m, res=None):
    if res is None:
        print(f"--- {m} ---")
    else:
        print(f"--- {m} --- STATUS: {res.status_code}")
        try:
            print(res.json())
        except:
            print(res.text)
        print()

def run():
    # 1. Register
    reg_data = {
        "username": "testuser_audit",
        "email": "audit@test.com",
        "password": "Password123!"
    }
    # To avoid failure if already exists, maybe append a random number
    import random
    reg_data['username'] += str(random.randint(1000,9999))
    res = requests.post(f"{BASE_URL}/users/register/", json=reg_data)
    p("REGISTER", res)
    if res.status_code != 201:
        return

    # 2. Login
    login_data = {
        "username": reg_data["username"],
        "password": reg_data["password"]
    }
    res = requests.post(f"{BASE_URL}/users/login/", json=login_data)
    p("LOGIN", res)
    token = res.json().get('access')
    headers = {'Authorization': f'Bearer {token}'}

    # 3. List Emotions
    res = requests.get(f"{BASE_URL}/devotional/emotions/", headers=headers)
    p("LIST EMOTIONS", res)

    # 4. Devotional by emotion (ansioso)
    res = requests.post(f"{BASE_URL}/devotional/by-emotion/", json={"emotion_slug": "ansioso"}, headers=headers)
    p("DEVOTIONAL BY EMOTION", res)
    devotional_data = res.json()
    ref_display = devotional_data.get('scripture_reference')

    # 5. Explain passage
    res = requests.post(f"{BASE_URL}/bible/explain/", json={"reference": ref_display}, headers=headers)
    p("EXPLAIN PASSAGE", res)

    # 6. Daily reflection
    res = requests.get(f"{BASE_URL}/reflection/daily/", headers=headers)
    p("DAILY REFLECTION", res)
    reflection_id = res.json().get('id')

    # 7. Answer reflection
    res = requests.post(f"{BASE_URL}/reflection/daily/{reflection_id}/answer/", json={"answer_text": "Senti muita paz lendo isso hoje."}, headers=headers)
    p("ANSWER REFLECTION", res)
    
    # 8. Feedback
    # Let's feedback the explain passage (it creates a GeneratedResponse)
    # Wait, explain doesn't return content_ref_id in the JSON. Does it? Let's check the API response.
    # Devotional by emotion might return a generated_response_id or something?
    # Let's feedback the AI core directly if we don't have the id yet, or let's inspect the payload first.
    
if __name__ == "__main__":
    run()
