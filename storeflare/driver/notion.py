from dotenv import load_dotenv
import requests
import hashlib
import json
import os 
import sys
from pydantic import BaseModel
from requests.auth import HTTPBasicAuth

load_dotenv()

NOTION_APIKEY=os.getenv("NOTION_APIKEY")
NOTION_DBID=os.getenv("NOTION_DBID")
NOTION_APIURL="https://api.notion.com/v1"
NOTION_HEADERS={
    "Authorization": f"Bearer {NOTION_APIKEY}",
    "Notion-Version": "2022-06-28"
}
NOTION_PAGES_PROPERTIES={}
payload={
    "offset": 0
}


class WebAnalytics(BaseModel):
    domain_name: str
    date: str
    page_views: float
    visits: float

def addTitle(value):
    return {
        "title":[
            {"text": {"content": value}}
        ]
    }

def addSelect(value):
    return {
        "select": {
            "name": value
        }
    }

def addMultiSelect(value):
    options = [{"name": opt.strip()} for opt in value.split(", ") if opt.strip()] if value is not None else ""
    return {
        "multi_select": options        
    }

def addDate(value):
    return {
        "date": { "start": value if value != None else None }
    }

def addRichText(value):
    return {
        "rich_text": [
            {"text": {"content": value}}
        ]
    }

def addURL(value):
    return {"url": value}

def addNumber(value):
    return {"number": value}

def addEmail(value):
    return {"email": value}

def addPhone(value):
    return {"phone_number": value}

def addCheckBox(value):
    if value == 'FALSE':
        value = False
    if value == 'TRUE':
        value = True 
    if value == None:
        value = False
    return {"checkbox": value }

def readValue(value):
    if value['type'] == "url":
        return value["url"]
    if value['type'] == "phone_number":
        return value["phone_number"]
    if value['type'] == "rich_text":
        return value["rich_text"][0]["plain_text"]
    if value["type"] == "select":
        return value["select"]["name"]
    if value["type"] == "multi_select":
        return ", ".join(item["name"] for item in value["multi_select"])
    if value["type"] == "email":
        return value["email"]
    if value["type"] == "title":
        return value["title"][0]["plain_text"]
    return ""

def setValue(dataType, value):
    if dataType == "url":
        return addURL(value)
    if dataType == "phone_number":
        return addPhone(value)
    if dataType == "rich_text":
        return addRichText(value)
    if dataType == "select":
        return addSelect(value)
    if dataType == "multi_select":
        return addMultiSelect(value)
    if dataType == "email":
        return addEmail(value)
    if dataType == "title":
        return addTitle(value)
    if dataType == "date":
        return addDate(value)
    if dataType == "number":
        return addNumber(value)
    return ""

def computeHash(data):
    jsonString = json.dumps(data, sort_keys=True)
    return hashlib.sha256(jsonString.encode()).hexdigest()

def get_database_properties():
    result = {}
    url = f"{NOTION_APIURL}/databases/{NOTION_DBID}"
    response = requests.get(url, headers=NOTION_HEADERS)

    if response.status_code == 200:
        database_info = response.json()
        properties = database_info.get("properties", {})

        result = {}

        for prop_name, prop_details in properties.items():
            result[prop_name] = prop_details

        return result
    else:
        print(f"Failed to fetch database properties: {response.text}")
        return None


def fetchAllNotionRecords():

    notion_records={}
    query_url = f"{NOTION_APIURL}/databases/{NOTION_DBID}/query"
    payload = {}

    while True:
        response = requests.post(query_url, headers=NOTION_HEADERS, json=payload)
        if response.status_code != 200:
            print(f"Error fetching Notion DB {NOTION_DBID}: {response.text}")
            break

        data = respones.json()
        for result in data["results"]:
            page_id = result['id']
            properties = result["properties"]
            name_property = properties["Name"]["title"]

            if name_property:
                name = name_property[0]["text"]["content"]
                notion_records[name] = {
                    "id": page_id,
                    "properties": properties    
                }

        if not data["has_more"]:
            break
        payload["start_cursor"] = data["next_cursor"]
    return notion_records

def fetch_unique_dates():
    """Fetch all records and return a sorted list of unique dates."""
    unique_dates = set()
    has_more = True
    next_cursor = None

    NOTION_QUERY_URL = f"{NOTION_APIURL}/databases/{NOTION_DBID}/query"

    while has_more:
        payload = {"page_size": 100}
        if next_cursor:
            payload["start_cursor"] = next_cursor

        response = requests.post(NOTION_QUERY_URL, headers=NOTION_HEADERS, json=payload)

        if response.status_code != 200:
            print(f"Error: Unable to fetch Notion data. Status Code: {response.status_code}")
            print("Response:", response.text)
            return []

        data = response.json()
        results = data.get("results", [])
        
        # Extract date values
        for record in results:
            properties = record.get("properties", {})
            date_field = properties.get("Date", {}).get("date", {}).get("start")
            if date_field:
                unique_dates.add(date_field)

        # Handle pagination
        has_more = data.get("has_more", False)
        next_cursor = data.get("next_cursor")

    # Convert to sorted list (oldest to newest)
    return sorted(unique_dates)

def getDateRange():
    dates = fetch_unique_dates()
    if not dates:
        return 0, 0
    return dates[0], dates[-1]  # Oldest, Newest

def createNewData(domain_name, dateMetric):
    createPayload = {
        "parent": {"database_id": NOTION_DBID},
        "properties": {
            "DomainName": setValue('title', domain_name),
            "Date": setValue('date', dateMetric['date']),
            "PageViews": setValue('number', dateMetric["metrics"]["page_views"]),
            "Visits": setValue('number', dateMetric["metrics"]["visits"])
        }
    }

    NOTION_QUERY_URL = f"{NOTION_APIURL}/databases/{NOTION_DBID}/query"
    saveData = requests.post(f"{NOTION_APIURL}/pages", headers=NOTION_HEADERS, json=createPayload)

    if saveData.status_code==200:
        return True
    else:
        raise ValueError(f"Can't get data with error code {saveData.text}")
        return False

    

def checkDomainEntry(domain_name, date):
    query_payload = {
        "filter": {
            "and": [
                {"property": "DomainName", "rich_text": {"equals": domain_name}},
                {"property": "Date", "date": {"equals": date}}
            ]
        }
    }

    NOTION_QUERY_URL = f"{NOTION_APIURL}/databases/{NOTION_DBID}/query"

    try:
        response = requests.post(NOTION_QUERY_URL, headers=NOTION_HEADERS, json=query_payload)

        if response.status_code != 200:
            raise ValueError("Error when querying the domain and data")

        data = response.json()
        if len(data['results']) > 0:
            return True 
            
        return False 

    except Exception as e:
        print(f"Error querying Notion database: {e}")
        return False

