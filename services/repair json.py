import json

file_name = "character.json"
with open(f"scraper_service/time_data/person_stats_pattern/{file_name}", "r", encoding="utf-8") as file:
    data = json.load(file)

print(data)
new_data = {
    "positive_traits": {},
    "negative_traits": {}
}

for kat in data:
    new_data["positive_traits"][kat] = [i for i in data[kat]["positive_traits"].keys()]
    new_data["negative_traits"][kat] = [i for i in data[kat]["negative_traits"].keys()]

print(new_data)

with open(f"scraper_service/time_data/person_stats_pattern/{file_name}", "w", encoding="utf-8") as file:
    json.dump(new_data, file, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    """
    it was a one-time script to repair json files
    """