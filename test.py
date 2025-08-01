import requests
import json

url = "http://127.0.0.1:5000/predict"

payload = {
    "LDA_PARTNUMBER": "5443"
}

response = requests.post(url, json=payload)

if response.ok:
    result = response.json()
    
    if "error" in result:
        print("❌ Error:", result["error"])
    else:
        print("✅ Prediction Summary for LDA:", payload["LDA_PARTNUMBER"])
        print(f"Predicted S1: {result['s1']}")
        print(f"Lower S1 Limit: {result['Lowest_S1']}  | Upper S1 Limit: {result['Upper_S1']}")
        print(f"Predicted S2: {result['s2']}")
        print(f"Lower S2 Limit: {result['Lowest_S2']}  | Upper S2 Limit: {result['Upper_S2']}")
else:
    print("❌ Failed to get response:", response.status_code, response.text)
