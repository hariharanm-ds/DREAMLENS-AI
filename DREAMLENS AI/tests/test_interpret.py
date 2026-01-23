import requests

URL = "http://127.0.0.1:5000/interpret"

examples = [
    "I was flying over the city and felt free",
    "I was chased by a snake through an alley",
    "My childhood home was burning and I couldn't get out",
]

for ex in examples:
    r = requests.post(URL, json={"dream": ex})
    print('Dream:', ex)
    print('Status:', r.status_code)
    try:
        print(r.json())
    except Exception as e:
        print('Error parsing JSON:', e)
    print('-' * 40)
