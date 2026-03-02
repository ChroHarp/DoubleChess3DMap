import urllib.request
import json

seq = "1,3,11,45,199,929,4505,22459"
url = f"https://oeis.org/search?q={seq}&fmt=json"

req = urllib.request.Request(
    url, 
    data=None, 
    headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
)

try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        if data:
            results = data
            for res in results:
                print(f"ID: A{res['number']:06d}")
                print(f"Name: {res['name']}")
                print(f"Data: {res['data']}")
                if 'formula' in res:
                    print("Formulas:")
                    for f in res['formula']:
                        print("  -", f)
                print("-" * 50)
        else:
            print("No matching sequence found in OEIS.")
except Exception as e:
    print("Error:", e)
