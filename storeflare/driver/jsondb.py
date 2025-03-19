import os

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional
from tinydb import TinyDB, Query
from dotenv import load_dotenv

load_dotenv()

CF_ACCOUNTID=os.getenv("CF_ACCOUNTID")
CF_ZONEID=os.getenv("CF_ZONEID")
DB_LOCATION=f"{os.getcwd()}/dumped_db"

class Metrics(BaseModel):
    page_views: Optional[float] = None
    visits: Optional[float]=None
    requests: Optional[float]=None

class DateEntry(BaseModel):
    date: str
    metrics: Metrics

class DomainEntry(BaseModel):
    name: str=Field(description="Domain Name")
    dates: List[DateEntry]

class DomainMetrics(BaseModel):
    domains: List[DomainEntry]

def createIfNotExists(location):
    if not os.path.exists(location):
        with open(location, "w") as f:
            f.write("{}")


WEB_ANAL_FILE = f"{DB_LOCATION}/{CF_ZONEID}_web_analytics.json"
OVERVIEW_FILE = f"{DB_LOCATION}/{CF_ZONEID}_overview.json" 
    
createIfNotExists(WEB_ANAL_FILE)
createIfNotExists(OVERVIEW_FILE)


def getDomainData(domain_name):
    db = TinyDB(WEB_ANAL_FILE)
    DomainQuery = Query()
    result = db.search(DomainQuery.name == domain_name)

    db.close()

    return result

def getDateDomain(domain_name, date):
    db = TinyDB(WEB_ANAL_FILE)

def insertDomain(domainEntry: DomainEntry):
    db = TinyDB(WEB_ANAL_FILE)
    inserted_id = db.insert(domainEntry)
    getStatus = db.get(doc_id=inserted_id)

    db.close()

    return getStatus

def insertDomainDate(domainName, dateEntry: DateEntry):
    db = TinyDB(WEB_ANAL_FILE)
    DomainQuery = Query()
    result = db.search(DomainQuery.name == domainName)
    if result:
        domainData = result[0]
        domainData["date_lists"].append(dateEntry["date"])
        domainData["dates"].append(dateEntry)
        db.update({"dates": domainData["dates"]}, DomainQuery.name == domainName)
        db.update({"date_lists": domainData["date_lists"]}, DomainQuery.name == domainname)
        return True
    return False

def getDateRange():
    db = TinyDB(WEB_ANAL_FILE)
    allDomain = db.all()
    allDates = []
    ymdformat = "%Y-%m-%d"

    for domain in allDomain:
        allDates.extend(domain["date_lists"])

    if not allDates:
        return [datetime.now().strftime(ymdformat), datetime.now().strftime(ymdformat)]

    dateObjects = [datetime.strptime(date, "%Y-%m-%d") for date in allDates]

    db.close()

    return [min(dateObjects).strftime(ymdformat), max(dateObjects).strftime(ymdformat)]

def getSecondNewestDate():
    db = TinyDB(WEB_ANAL_FILE)
    allDomains = db.all()
    allDates = []
    # Collect all dates
    for domain in allDomains:
        allDates.extend(domain["date_lists"]) 

    if len(allDates) < 2:
         return None
    
    date_objects = sorted([datetime.strptime(date, "%Y-%m-%d") for date in allDates], reverse=True)

    second_newest_date = date_objects[1]  # Get the second newest date
    return second_newest_date.strftime("%Y-%m-%d") 

