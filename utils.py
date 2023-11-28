from datetime import datetime

BASEURLSTR = "https://advisories.ncsc.nl/ajax/search?from=%s&to=%s&words=&prob[]=%s&dmg[]=%s"
CURRENTMONTH= datetime.now().strftime('%m')
CURRENTYEAR = datetime.now().year

#returns an array with two URL's
#we break up the months in two to avoid making a too big request (which is the occasionally the case if you make a request for the whole month)
def createURLsForMonth(year, iMonth, prob, dmg) : 
    pairOfUrls = []
    startdate1 = "01-%s-%s" % (f"{iMonth:02d}",year)
    endate1 = "15-%s-%s" % (f"{iMonth:02d}",year)
    
    startdate2 = "15-%s-%s" % (f"{iMonth:02d}",year)
    nextmonth = iMonth+1
    if iMonth==12 : 
        nextmonth = 1
        year = year+1
    endate2 = "01-%s-%s" % (f"{nextmonth:02d}",year)
    
    url1 = BASEURLSTR % (startdate1, endate1, prob, dmg) 
    url2 = BASEURLSTR % (startdate2, endate2, prob, dmg)

    pairOfUrls.append(url1)
    pairOfUrls.append(url2)

    return pairOfUrls

def createURLsForYear(year, prob, dmg) : 
    setOfURLs = []

    if year > int(CURRENTYEAR) :
        print("only current year or older (starting 2014)!")
        return setOfURLs
    
    for i in range(1,13,1):

        if(i > int(CURRENTMONTH) and year >= int(CURRENTYEAR)) :
            print("Skipping month %s (%s) as it is in the future" % (i, year))
        else :
            pairOfURLs = createURLsForMonth(year,i,prob,dmg)
            #append this array the Python way:
            setOfURLs = setOfURLs + pairOfURLs
        
    return setOfURLs

#little test code
""" urls = createURLsForYear("2022", "medium", "high")
for url in urls:
    print(url) """