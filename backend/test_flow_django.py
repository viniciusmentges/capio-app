import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

def p(m, res=None):
    if res is None:
        print(f"--- {m} ---")
    else:
        print(f"--- {m} --- STATUS: {res.status_code}")
        try:
            print(json.dumps(res.json(), indent=2, ensure_ascii=False))
        except:
            if b'Exception Value' in res.content:
                print("HTML Error intercepted:")
                text = res.content.decode()
                import re
                m = re.search(r'<pre class="exception_value">(.*?)</pre>', text, re.S)
                if m: print(m.group(1).strip())
                else: print("Could not parse exception.")
            else:
                print(res.content.decode('utf-8')[:500])
        print()

def run():
    client = Client(SERVER_NAME='localhost')
    
    # 1. Register
    reg_data = {
        "username": "testuser_audit",
        "email": "audit@test.com",
        "password": "Password123!"
    }
    import random
    rand_str = str(random.randint(1000,9999))
    reg_data['username'] += rand_str
    reg_data['email'] = f"audit{rand_str}@test.com"
    res = client.post("/api/auth/register/", data=json.dumps(reg_data), content_type='application/json', HTTP_ACCEPT='application/json')
    p("REGISTER", res)
    if res.status_code != 201:
        return

    # 2. Login
    login_data = {
        "username": reg_data["username"],
        "password": reg_data["password"]
    }
    res = client.post("/api/auth/login/", data=json.dumps(login_data), content_type='application/json', HTTP_ACCEPT='application/json')
    p("LOGIN", res)
    token = res.json().get('access')
    auth_headers = {'HTTP_AUTHORIZATION': f'Bearer {token}'}

    # 3. List Emotions
    res = client.get("/api/devotional/emotions/", **auth_headers)
    p("LIST EMOTIONS", res)

    # 4. Devotional by emotion (ansioso)
    res = client.post("/api/devotional/by-emotion/", data=json.dumps({"emotion_slug": "ansioso"}), content_type='application/json', **auth_headers)
    p("DEVOTIONAL BY EMOTION", res)
    devotional_data = res.json()
    ref_display = devotional_data.get('scripture_reference')
    # Let's verify what data is returned here. Should only be clean data.

    # 5. Explain passage
    res = client.post("/api/bible/explain/", data=json.dumps({"reference": ref_display}), content_type='application/json', **auth_headers)
    p("EXPLAIN PASSAGE", res)

    # 6. Daily reflection
    res = client.get("/api/reflection/today/", **auth_headers)
    p("DAILY REFLECTION", res)
    reflection_data = res.json()

    # 7. Answer reflection
    res = client.post(f"/api/reflection/today/respond/", data=json.dumps({"answer_text": "Senti muita paz lendo isso hoje."}), content_type='application/json', **auth_headers)
    p("ANSWER REFLECTION", res)
    
if __name__ == "__main__":
    run()
