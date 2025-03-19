import os
import sys

import cfmetrics
from datetime import datetime, timedelta
from dotenv import load_dotenv
from driver import jsondb, sqlite, notion
from transform import checkAnalAndStore, checkOverview

load_dotenv()

CF_API_KEY=os.getenv("CF_API_KEY")
CF_EMAIL=os.getenv("CF_EMAIL")
CF_ACCOUNTID=os.getenv("CF_ACCOUNTID")
CF_ZONEID=os.getenv("CF_ZONEID")
NOTION_WEBANAL_DBID=os.getenv("NOTION_WEBANAL_DBID")
NOTION_OVERVIEW_DBID=os.getenv("NOTION_OVERVIEW_DBID")

def main():
    if len(sys.argv) < 2:
        print("Usage: python cli.py <targetdb[json|sqlite]>")
        sys.exit(1)
    cmd = sys.argv[1]

    if cmd not in ["json", "sqlite", "notion"]:
        print("Usage: python cli.py <targetdb[json|sqlite]>")
        sys.exit(1)

    ymdformat = "%Y-%m-%d"
    cf = cfmetrics.Auth(CF_API_KEY, CF_EMAIL).Account(CF_ACCOUNTID).Zone(CF_ZONEID)

    # Lets Provide the Web Analytic First
    # need to check the database first
    # if the 30 days data is already stored or not
    # if already stored, check today data and stored
    # if not then stored for 30 days before
    source = ["web_analytics", "overview"]
    NOTION_DBID = [NOTION_WEBANAL_DBID, NOTION_OVERVIEW_DBID]

    for index, srcNotion in enumerate(NOTION_DBID):

        print(f"get {source[index]}")

        oldest_date, newest_date = [datetime.now().strftime(ymdformat), datetime.now().strftime(ymdformat)]
        if cmd == "json":
            oldest_date, newest_date = jsondb.getDateRange()
        if cmd == "sqlite":
            oldest_date, newest_date = sqlite.getDateRange(source[index])
        if cmd == "notion":
            oldest_date, newest_date = notion.getDateRange(srcNotion)

        print("Proceed to check today data and update the data")
    
        daysDifference = (datetime.strptime(newest_date,"%Y-%m-%d")- datetime.strptime(oldest_date,"%Y-%m-%d")).days

        print(f"Latest Data tooks {daysDifference} from {oldest_date} to {newest_date}")
        
        if daysDifference < 30:
            #dateFormat = "%Y-%m-%dT%H:%M:%SZ"
            #startDate = f"2025-01-01T00:00:01Z"
            #endDate = datetime.now().strftime(dateFormat)

            print("There is no data, lets get 30 days from today")
            if source[index] == "web_analytics":
                getWebAnal = cf.get_web_analytics()
                if len(getWebAnal['by_domain']['domains']) >0:
                    checkAnalAndStore(getWebAnal, cmd)
                else:
                    print("No Data")

            elif source[index] == "overview":
                getData = cf.get_overview()
                if len(getData['by_date']['date_lists']) >0:
                    checkOverview(getData, cmd)
                else:
                    print("No Data")
            
        # only get today
        else:
            if newest_date == datetime.now().strftime("%Y-%m-%d"):
                print("Data is updated")
                continue

            dateFormat = "%Y-%m-%dT%H:%M:%SZ"
            startDate = f"{jsondb.getSecondNewestDate()}T00:00:01Z"
            #startDate = f"2025-01-01T00:00:01Z"
            endDate = datetime.now().strftime(dateFormat)

            print(f"Get data from {startDate} to {endDate}")
            getWebAnal = cf.get_web_analytics(start_date=startDate, end_date=endDate)

            checkAnalAndStore(getWebAnal, cmd)


if __name__ == "__main__":
    main()



    
