print "POODLE"
print "-----"
import urllib2
import pickle

# ----- CRAWLER ----- #
#__GLOBALS__
MAX_DEPTH = 2
urlGraph = {}   #Store EVERY URL contained by each URL
crawled=[]      #Store Unique URLs visited

#__INTERACE__
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

#__IMPLEMENTATION__
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
                        closeTag=html.find("</a>",aTag)
                        pos=closeTag+1
                else:
                        allFound=True   

        urlGraph[page] = allLinks
        return links



# ----- /CRAWLER ----- #

# ----- SCRAPER ----- # #Indexes unique words from a set of urls 
#__GLOBALS__
index = {}
pageWords = []

#__INTERFACE__
def scrape(urls):   #creates an index and saves in a file
        for url in urls:
                #get Page text for the current url
                pageWords = getPageText(url)
                #add page to index - correspond to keyword
                addPageToIndex(index,pageWords,url)
        fout = open("index.txt", "w")
        pickle.dump(index, fout)
        fout.close()
        

#__IMPLEMENTATION__
def getPageText(url):   #Gets every unique word on a page
	response = urllib2.urlopen(url)
	html = response.read()

	pageText,pageWords="",[]
	html=html[html.find("<body")+5:html.find("</body>")]

	startScript=html.find("<script")
	while startScript>-1:
		endScript=html.find("</script>")
		html=html[:startScript]+html[endScript+9:]
		startScript=html.find("<script")
    
	ignore=[]
	fin=open("ignorelist.txt","r")
	for word in fin:
		ignore.append(word.strip())
	fin.close()
    	
	finished=False
	while not finished:
		nextCloseTag=html.find(">")
		nextOpenTag=html.find("<")
		if nextOpenTag>-1:
			content=" ".join(html[nextCloseTag+1:nextOpenTag].strip().split())
			pageText=pageText+" "+content
			html=html[nextOpenTag+1:]
		else:
			finished=True
		
	for word in pageText.split():
		if word[0].isalnum() and not word in ignore:
			if not word in pageWords:
				pageWords.append(word)
	
	return pageWords

def addPageToIndex (index,pageWords,url):       #Page added "implicitly"
	for word in pageWords:  #for each unique word on the current page
		addWordToIndex(index,word,url)  #add the word to the scraper's index

def addWordToIndex(index,word,url):
        if word in index:
                index[word].append(url) #go to Key: "Word", add the current page URL
        else:
                index[word] = [url]               

# ----- /SCRAPER ----- #

# ----- PAGE RANKER ----- #
#__GLOBALS__
pageRanks = {}

def rankPages(graph):
    d=0.85
    numLoops=10
    npages=len(graph)
    ranks = {}
    
    for page in graph:
        ranks[page]=1.0/npages
    
    for i in range(0,numLoops):
        newRanks={}
        for page in graph:
            newRank=(1-d)/npages
            for node in graph:
                if page in graph[node]:
                    newRank=newRank+d*(ranks[node]/len(graph[node]))
            newRanks[page]=newRank
        ranks=newRanks
    return ranks
# ----- /PAGE RANKER ----- #


#MAIN#
crawl("http://193.61.191.117/~B00664468/COM%20506%20-%20Professional%20Web%20Services%20Dev/B3/test_web/test_index.html")
scrape(crawled)
pageRanks = rankPages(urlGraph)
