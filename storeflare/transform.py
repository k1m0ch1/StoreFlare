import sys
import os

from driver import jsondb, sqlite, notion
from dotenv import load_dotenv

load_dotenv()

NOTION_WEBANAL_DBID=os.getenv("NOTION_WEBANAL_DBID")
NOTION_OVERVIEW_DBID=os.getenv("NOTION_OVERVIEW_DBID")

availableCMD = ["json", "sqlite", "notion"]

def checkOverview(dataOverview, cmd):
    if cmd == "notion":
        print("Checkup and Insert data overview to notion")

        for date in dataOverview['by_date']['dates']:
            currentDateLists = notion.fetch_unique_dates(NOTION_OVERVIEW_DBID)
            if date['date'] not in currentDateLists:
                saveData = notion.createDataOverview(date, NOTION_OVERVIEW_DBID)
                if saveData == False:
                    print("Error Create New Data")
                else:
                    print("Create New Data")
 

def checkAnalAndStore(dataAnal, cmd):
    if cmd not in availableCMD:
        print("Usage: python cli.py <targetdb[json|sqlite]>")
        sys.exit(1)

    getWebAnal = dataAnal

    if cmd == "notion":
        print("Checkup and insert Data using Notion")
        for domain in getWebAnal['by_domain']['domains']:
            for date in domain['date_lists']:
                iD = domain['date_lists'].index(date)
                if notion.checkDomainEntry(domain['name'], date, NOTION_WEBANAL_DBID) == False:
                    saveData = notion.createDataWebAnalytics(domain['name'], domain['dates'][iD], NOTION_WEBANAL_DBID)
                    if saveData == False:
                        print("Error Create New Data")
                    else:
                        print("Create New Data")
        return True

    if cmd == "sqlite":
        for domain in getWebAnal['by_domain']['domains']:
            domainName = domain['name']
            for item in domain['dates']:
                if sqlite.getDomainDate(domainName, item['date'], 'web_analytics') == None:
                    dataWebAnalytics = sqlite.WebAnalytics(
                        domain_name=domain["name"],
                        date=item["date"],
                        page_views=item["metrics"]["page_views"],
                        visits=item["metrics"]["visits"]
                    )
                    saveData = sqlite.insertWebAnalytics(dataWebAnalytics)

    if cmd == "json":
        for domain in getWebAnal['by_domain']['domains']:
            domainData = jsondb.getDomainData(domain['name'])

            if len(domainData) == 0:
                saveData = jsondb.insertDomain(domain)
            else:
                for domain in domainData:
                    for datedb in domain['date_lists']:
                        cdI = domain['date_lists'].index(datedb)
                        if datedb not in domain['date_lists']:
                            print("insert New Data")
                            saveData = jsondb.insertDomainDate(domain["name"], domain['dates'][cdI])

