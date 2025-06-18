import os
import json
import random
from bson import ObjectId
from dotenv import load_dotenv
from pymongo import MongoClient

# ---------- CONFIG ----------
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
MONGO_URI = os.getenv("MONGO_DB_URI")
DB_NAME = "healthsutra"
COLLECTION_NAME = "test_history"
JSON_INPUT_PATH = "./extracted_report.json"

# ---------- CONNECT ----------
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# ---------- LOAD EXTRACTED JSON ----------
with open(JSON_INPUT_PATH, "r", encoding="utf-8") as f:
    extracted = json.load(f)

# ---------- EXTRACT REQUIRED DATA ----------
report_type = "pathology" if any(t["testType"] == "pathlab" for t in extracted["tests"]) else "radiology"
patient_name = extracted["reportDetails"]["patientDetails"]["name"]
metadata = extracted["reportDetails"]["reportMetadata"]

# ---------- FIND EXISTING USER OR ASSIGN RANDOM ----------
existing_doc = collection.find_one({"patient_name": patient_name})
user_id = existing_doc["user_id"] if existing_doc else f"user_{random.randint(10000, 99999)}"

# ---------- TRANSFORM TESTS ----------
tests_transformed = []
for test in extracted["tests"]:
    test_obj = {
        "testCategory": test["testCategory"],
        "sampleType": test.get("sampleType"),
        "testType": test["testType"],
        "testDetails": []
    }

    for td in test["testDetails"]:
        if test["testType"] == "pathlab":
            test_obj["testDetails"].append({
                "testName": td["testName"],
                "result": {
                    "value": td["result"]["value"],
                    "unit": td["result"]["unit"],
                    "flag": td["result"]["flag"]
                },
                "outOfRange": td["outOfRange"]
            })
        elif test["testType"] == "radiology":
            test_obj["testDetails"].append({
                "organName": td["organName"],
                "outOfRange": td["outOfRange"]
            })

    tests_transformed.append(test_obj)

# ---------- CREATE FINAL DOCUMENT ----------
report_history_doc = {
    "_id": ObjectId(),
    "reportId": f"rep_{random.randint(100000, 999999)}",
    "user_id": user_id,
    "patient_name": patient_name,
    "reportType": report_type,
    "metadata": {
        "collectionDate": metadata["collectionDateTime"],
        "reportDateTime": metadata["reportDateTime"],
        "receivingDateTime": metadata["receivingDateTime"],
        "reportStatus": metadata["reportStatus"]
    },
    "tests": tests_transformed
}

# ---------- INSERT INTO DB ----------
collection.insert_one(report_history_doc)
print(f"Inserted report for user {user_id} with reportId: {report_history_doc['reportId']}")
