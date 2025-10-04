import json



with open("db.json", "r", encoding="utf-8") as f:
    db = json.load(f)

posts = db["General Grievous"]["emotions"]["opinion"]
analyzed_data = []
