import sys

from driver import jsondb, sqlite

def checkAnalAndStore(dataAnal, cmd):

    availableCMD = ["json", "sqlite"]
    
    if cmd not in availableCMD:
        print("Usage: python cli.py <targetdb[json|sqlite]>")
        sys.exit(1)

    getWebAnal = dataAnal
    # store the data to database
    for domain in getWebAnal['by_domain']['domain_lists']:
        # check if domain already exist or not
            
        if cmd == "sqlite":
            domainData = sqlite.getDomainData(domain, "web_analytics")
        elif cmd == "json":
            domainData = jsondb.getDomainData(domain)
        else:
            domainData = None

        dI = getWebAnal['by_domain']['domain_lists'].index(domain)
        currentDomain = getWebAnal['by_domain']['domains'][dI]
        if len(domainData) == 0:
            # insert if not exists
            if cmd == "sqlite":
                for item in currentDomain['dates']:
                    dataWebAnalytics = sqlite.WebAnalytics(
                        domain_name=currentDomain["name"],
                        date=item["date"],
                        page_views=item["metrics"]["page_views"],
                        visits=item["metrics"]["visits"]
                    )
                    saveData = sqlite.insertWebAnalytics(dataWebAnalytics)
            elif cmd == "json":
               saveData = jsondb.insertDomain(currentDomain) 
        else:
            # check if the data is that pulled is have a new data or not
            # not yet tested
            if cmd == "sqlite":
                date_lists = [item[0] for item in domainData]
                for datesource in currentDomain["date_lists"]:
                    if datesource not in date_lists:
                        for item in currentDomain['dates']:
                            dataWebAnalytics = sqlite.WebAnalytics(
                                domain_name=currentDomain["name"],
                                date=item["date"],
                                page_views=item["metrics"]["page_views"],
                                visits=item["metrics"]["visits"]
                            )
                            saveData = sqlite.insertWebAnalytics(dataWebAnalytics)

            elif cmd == "json":

                for domain in domainData:
                    for datedb in currentDomain['date_lists']:
                        cdI = currentDomain['date_lists'].index(datedb)
                        if datedb not in datedb['date_lists']:
                            saveData = jsondb.insertDomainDate(currentDomain["name"], currentDomain['dates'][cdI])

