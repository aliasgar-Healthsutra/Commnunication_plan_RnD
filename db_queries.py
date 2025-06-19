import json
import os
from pymongo import MongoClient
from dotenv import load_dotenv
import json
from datetime import datetime

# MongoDB setup
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
MONGO_URI = os.getenv("MONGO_DB_URI")
DB_NAME = "healthsutra"
COLLECTION_NAME = "reports"
client = MongoClient(MONGO_URI)
collection = client[DB_NAME][COLLECTION_NAME]

# Inputs (example values)
target_user_id = "67b167fb429d87adc4346b15"
test_name = "T3 (TRIODOTHYRONINE), SERUM"
#organ_name = "Liver"

#pagination parameters (if used)
page = 1
page_size = 10


# utity functions
def normalize(docs):
    for doc in docs:
        if "_id" in doc:
            doc["_id"] = str(doc["_id"])
    return docs

def convert_datetime(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

# Query to get all reports ever stored in the database
query0 = list(collection.find({}))

def generate_user_report_pipeline(
    user_id: str,
    match_stage: dict = None,
    sort_stage: dict = None,
    skip: int = None,
    limit: int = None,
    projection: dict = None
):
    pipeline = [
        {"$match": {"UserID": user_id}},
        {"$unwind": "$tests"},
        {"$unwind": "$tests.testDetails"},
    ]

    if match_stage:
        pipeline.append({"$match": match_stage})

    pipeline.append({"$project": projection or {
        "_id": 0,
        "UserID": 1,
        "reportDateTime": "$reportDetails.reportMetadata.reportDateTime",
        "testName": "$tests.testDetails.testName",
        "result.value": "$tests.testDetails.result.value",
        "result.unit": "$tests.testDetails.result.unit",
        "result.flag": "$tests.testDetails.result.flag",
        "outOfRange": "$tests.testDetails.outOfRange"
    }})

    if sort_stage:
        pipeline.append({"$sort": sort_stage})
    if skip is not None:
        pipeline.append({"$skip": skip})
    if limit is not None:
        pipeline.append({"$limit": limit})

    return pipeline

def get_user_reports(user_id: str):
    pipeline = generate_user_report_pipeline(user_id)
    return list(collection.aggregate(pipeline))

def get_user_reports_sorted(user_id: str, ascending: bool = True):
    sort_order = 1 if ascending else -1
    pipeline = generate_user_report_pipeline(user_id, sort_stage={"reportDateTime": sort_order})
    return list(collection.aggregate(pipeline))

def get_specific_test_reports(user_id: str, test_name: str, ascending: bool = True):
    sort_order = 1 if ascending else -1
    match_stage = {"tests.testDetails.testName": test_name}
    pipeline = generate_user_report_pipeline(user_id, match_stage=match_stage, sort_stage={"reportDateTime": sort_order})
    return list(collection.aggregate(pipeline))

def get_out_of_range_tests(user_id: str):
    match_stage = {"tests.testDetails.outOfRange": True}
    pipeline = generate_user_report_pipeline(user_id, match_stage=match_stage, sort_stage={"reportDateTime": -1})
    return list(collection.aggregate(pipeline))

def get_user_reports_paginated(user_id: str, page: int = 1, limit: int = 10):
    skip = (page - 1) * limit
    pipeline = generate_user_report_pipeline(
        user_id,
        sort_stage={"reportDateTime": -1},
        skip=skip,
        limit=limit
    )
    return list(collection.aggregate(pipeline))

# Write output
output = {
    "query1_all_reports_filtered": normalize(get_user_reports(target_user_id)),
    "query2_sorted_by_reportDateTime": normalize(get_user_reports_sorted(target_user_id, ascending=False)),
    "query3_specific_test_sorted": normalize(get_specific_test_reports(target_user_id, test_name, ascending=False)),
    "query4_out_of_range_test": normalize(get_out_of_range_tests(target_user_id)),
    "query5_paginated_results": normalize(get_user_reports_paginated(target_user_id, page, page_size))

}

with open("./query_results_output.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, default=convert_datetime)


print("✅ Query results written to query_results_output.json")
