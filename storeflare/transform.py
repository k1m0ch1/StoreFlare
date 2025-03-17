import sys

from driver import jsondb, sqlite, notion

def checkAnalAndStore(dataAnal, cmd):

    availableCMD = ["json", "sqlite", "notion"]
    
    if cmd not in availableCMD:
        print("Usage: python cli.py <targetdb[json|sqlite]>")
        sys.exit(1)

    getWebAnal = dataAnal

    if cmd == "notion":
        print("Checkup and insert Data using Notion")
        for domain in getWebAnal['by_domain']['domains']:
            for date in domain['date_lists']:
                iD = domain['date_lists'].index(date)
                if notion.checkDomainEntry(domain['name'], date) == False:
                    saveData = notion.createNewData(domain['name'], domain['dates'][iD]) 
                    if saveData == False:
                        print("Error Create New Data")
                    else:
                        print("Create New Data")
        return True

    if cmd == "sqlite":
        for domain in getWebAnal['by_domain']['domains']:
            for item in domain['dates']:
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

