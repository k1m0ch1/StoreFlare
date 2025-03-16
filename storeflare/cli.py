import os
import sys

import cfmetrics
from datetime import datetime, timedelta
from dotenv import load_dotenv
from driver import jsondb

load_dotenv()

CF_API_KEY=os.getenv("CF_API_KEY")
CF_EMAIL=os.getenv("CF_EMAIL")
CF_ACCOUNTID=os.getenv("CF_ACCOUNTID")
CF_ZONEID=os.getenv("CF_ZONEID")

def checkAnalAndStore(dataAnal):
   # store the data to database
   for domain in getWebAnal['by_domain']['domain_lists']:
       # check if domain already exist or not
       domainData = jsondb.getDomain(domain)
       dI = getWebAnal['by_domain']['domain_lists'].index(domain)
       currentDomain = getWebAnal['by_domain']['domains'][dI]
       if len(domainData) == 0:
           # insert if not exists
           saveData = jsondb.insertDomain(currentDomain) 
       else:
           # check if the data is that pulled is have a new data or not
           # not yet tested
           for domain in domainData:
               for datedb in currentDomain['date_lists']:
                   cdI = currentDomain['date_lists'].index(datedb)
                   if datedb not in datedb['date_lists']:
                        saveData = jsondb.insertDomainDate(currentDomain["name"], currentDomain['dates'][cdI])
 

# need to check the database first
# if the 30 days data is already stored or not
# if already stored, check today data and stored
# if not then stored for 30 days before
cf = cfmetrics.Auth(CF_API_KEY, CF_EMAIL).Account(CF_ACCOUNTID).Zone(CF_ZONEID)
mantap = cf.get_overview()

oldest_date, newest_date = jsondb.getDateRange()
if newest_date == datetime.now().strftime("%Y-%m-%d"):
    print("Data is updated, end the program")
    sys.exit(1)

print("Proceed to check today data and update the data")

daysDifference = (datetime.strptime(newest_date,"%Y-%m-%d")- datetime.strptime(oldest_date,"%Y-%m-%d")).days

if daysDifference < 30:
    getWebAnal = cf.get_web_analytics()

    if len(getWebAnal['by_domain']['dates']) >0:
        checkAnalAndStore(getWebAnal)
    else:
        print("No Data")

# only get today
else:
    dateFormat = "%Y-%m-%dT%H:%M:%SZ"
    startDate = f"{jsondb.getSecondNewestDate()}T23:59:59Z"
    endDate = datetime.now().strftime(dateFormat)

    print(f"Get data from {startDate} to {endDate}")
    getWebAnal = cf.get_web_analytics(start_date=startDate, end_date=endDate)

    checkAnalAndStore(getWebAnal)


    
