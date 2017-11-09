print "POODLE"
print "-----"
import urllib2

# ----- CRAWLER ----- #
MAX_DEPTH = 2
urlGraph = {}   #Store EVERY URL contained by each URL
crawled=[]      #Store Unique URLs visited

#Gets returns unseen links on each page
#Assigns all links to the global url graph
def getLinksOnPage(page,prevLinks):
        response = urllib2.urlopen(page)
        html = response.read()

        allLinks,links,pos,allFound=[],[],0,False
        while not allFound:
                aTag=html.find("<a href=",pos)
                if aTag>-1:
                        href=html.find('"',aTag+1)
                        endHref=html.find('"',href+1)
                        url=html[href+1:endHref]
                        if url[:7]=="http://":
                                if url[-1]=="/":
                                        url=url[:-1]

                                allLinks.append(url)    #store ALL links
                                if not url in links and not url in prevLinks:   #store UNIQUE links
                                        links.append(url)     
                                        print "Unseen URL Found: " + url
                        closeTag=html.find("</a>",aTag)
                        pos=closeTag+1
                else:
                        allFound=True   

        urlGraph[page] = allLinks
        return links

def crawl(urlSeed):
    toCrawl=[[urlSeed,0]] #becomes a list of lists - each element in the list is a list containing two items, URL and depth location.
    while toCrawl:
        nextPage = toCrawl.pop()#Get "hub" url and its depth level (depth x+1)
        nextURL = nextPage[0]   #Retrieve URL
        nextIndex = nextPage[1] #Retrieve URL depth
        
        crawled.append(nextURL) #Record that we have crawled the url(doing it now...)

        if nextIndex < MAX_DEPTH:
                newLinks = getLinksOnPage(nextURL, crawled)  #find all links at depth x      
                for links in newLinks:
                        toCrawl.append([links, nextIndex+1])    #found links are x+1 deep

# ----- /CRAWLER ----- #

# ----- SCRAPER ----- # #Indexes unique words from a set of urls 
index = {}
pageWords = []

def scrape(urls):
        for url in urls:
                #get Page text
                #add page to index


# ----- /SCRAPER ----- #

#MAIN#
crawl("http://193.61.191.117/~B00664468/COM%20506%20-%20Professional%20Web%20Services%20Dev/B3/test_web/test_index.html")
#TODO: Scraper: index unique words from urls found (use unique urls for performance)
#scrape(crawled)

#TODO: PageRank: use url graph to calculate page weights
