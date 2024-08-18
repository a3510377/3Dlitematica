import json

from t3dlitematica import resolve

data = resolve("./finalfinaltest.litematic")
with open("./test.json", "w", encoding="utf8") as f:
    json.dump(data, f, indent=4)
