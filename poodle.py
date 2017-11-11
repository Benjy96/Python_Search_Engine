import urllib2
import pickle
import random
import sys
import string

# ----- CRAWLER ----- #
#__GLOBALS__
MAX_DEPTH = 3
urlGraph = {}   #Store EVERY URL contained by each URL {Key: [url1, url2, url3, etc]}
crawled=[]      #Store Unique URLs visited

#__INTERACE__
def crawl(urlSeed, debug):
    toCrawl=[[urlSeed,0]] #becomes a list of lists - each element in the list is a list containing two items, URL and depth location.
    while toCrawl:
        nextPage = toCrawl.pop()#Get "hub" url and its depth level (depth x+1)
        nextURL = nextPage[0]   #Retrieve URL
        nextIndex = nextPage[1] #Retrieve URL depth
        
        #crawled.append(nextURL) #Record that we have crawled the url(doing it now...)
        if nextIndex < MAX_DEPTH:
                newLinks = getLinksOnPage(nextURL, crawled, debug)  #find all links at depth x
                crawled.append(nextURL)
                for links in newLinks:
                        toCrawl.append([links, nextIndex+1])    #found links are x+1 deep

#__IMPLEMENTATION__
#Gets returns unseen links on each page
#Assigns all links to the global url graph
def getLinksOnPage(page,prevLinks,debug):
        response = urllib2.urlopen(page)
        html = response.read()
        if debug == True:
            print "page " + page

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

        global urlGraph
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
    
	ignore=set()
	fin=open("ignore.txt","r")
	for word in fin:
		ignore.add(word.strip())
	fin.close()
    	
	finished=False
	while not finished:
		nextCloseTag=html.find(">")
		nextOpenTag=html.find("<")
		if nextOpenTag>-1:
			content=" ".join(html[nextCloseTag+1:nextOpenTag].strip().split())
			#Remove punctuation
			content = content.translate(None, string.punctuation)
			if content not in ignore:
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

#__INTERFACE__
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

# ----- POODLE ----- #
#__GLOBALS__
MAX_RESULTS_DISPLAYED = 10
DEBUG_MODE = False
cool_facts = ["POODLE rhymes with google. That type of rhyme is called assonance!", "POODLEs are ghastly looking dogs",
              "POODLE is going to get me 100% on my coursework!", "POODLE knows what you did last summer, if you put it online, that is..."]

def poodleOutput(pString):
    print "\nPOODLE: %s" % (pString) 

def poodleSetup():
    rand = random.randint(0,len(cool_facts)-1)
    print cool_facts[rand]
    print "-----"    
    
def poodleHelp():
    print ""
    print "POODLE Functionality:"
    print "-build\t\tCreate a POODLE database (and set the depth of the web crawler)"
    print "-dump\t\tSave the POODLE database you built"
    print "-search\t\tSet the maximum results returned by POODLE"
    print "-debug\t\tSet POODLE's debug mode (enables under the hood printing)"
    print "-restore\tRetrieve the last saved POODLE database"
    print "-print\t\tShow the POODLE database (index, graph, and page ranks)"
    print "-ignore\t\tPrint POODLE's ignore list"
    print "-help\t\tWhat do you think you're looking at, pal?"
    print "-exit\t\tExit the world as we know it!"

def poodleBuild():
    poodleOutput("Give me a seed URL! >>")
    crawl_seed = raw_input().strip()
    poodleOutput("Please set a maximum depth for the web crawl procedure! >>")

    global MAX_DEPTH
    depthSet = False
    while depthSet != True:
        depth_input = raw_input().strip()
        if depth_input.isdigit():
            try:
                depthSet = True
                MAX_DEPTH = int(depth_input)
            except:
                depthSet = False
    
    crawl(crawl_seed, DEBUG_MODE)
    poodleOutput("\n----- CRAWLED PAGES -----")
    for url in crawled:
        print url
    poodleOutput("Database created!")
    scrape(crawled)
    global pageRanks
    pageRanks = rankPages(urlGraph)

    #create a case-insensitive index
    global index    
    tempIndex = {}
    for word in index:
        tempIndex[word.lower()] = index[word]

    del index
    index = tempIndex

def poodleDump():   #heh
    #Save Crawled Index
    fout = open("graph.txt", "w")
    pickle.dump(urlGraph, fout)
    fout.close()

    #Save Scraped Index
    fout = open("index.txt", "w")
    pickle.dump(index, fout)
    fout.close()

    #Save Page Ranks
    fout = open("ranks.txt", "w")
    pickle.dump(pageRanks, fout)
    fout.close()

    poodleOutput("Database saved!")

def poodleRestore():
    #Load Crawled Index
    fin = open("graph.txt", "r")
    global urlGraph
    urlGraph = pickle.load(fin)
    fin.close()

    #Load Scraped Index
    fin = open("index.txt", "r")
    global index
    index = pickle.load(fin)
    fin.close()

    #Load PageRank Values
    fin = open("ranks.txt", "r")
    global pageRanks
    pageRanks = pickle.load(fin)
    fin.close()

    poodleOutput("Database loaded!")

def poodlePrint():
    poodleOutput("----- INDEXED WORDS & RESPECTIVE LOCATIONS -----")
    for keyword in index:
        print "{}: {}".format(keyword, index[keyword])

    poodleOutput("----- URL GRAPH -----")
    for page in urlGraph:
        print "PAGE: {}\n".format(page)
        print "\t{}\n".format(urlGraph[page])

    poodleOutput("----- PAGE RANKS -----")
    for url in pageRanks:
        print "{} | RANK: {}".format(url, pageRanks[url])

def poodleIgnoreList():
	fin = open("ignore.txt", "r")
	for word in fin:
		print word.strip()
	fin.close()

def poodleSetMaxResults():
	global MAX_RESULTS_DISPLAYED
	poodleOutput("Please set a maximum depth for the web crawl procedure! >>")

	maxDisplayedSet = False
	while maxDisplayedSet != True:
		user_input = raw_input().strip()
		if user_input.isdigit():
			try:
				maxDisplayedSet = True
				MAX_RESULTS_DISPLAYED = int(user_input)
			except:
				maxDisplayedSet = False;

def poodleDebug():
    global DEBUG_MODE
    poodleOutput("Current Debug Mode: {}".format(DEBUG_MODE))
    changeDebug = False;
    while changeDebug == False:
        poodleOutput("Set the debug mode? (yes or no) >>")
        user_input = raw_input().strip()
        if user_input.lower() == "yes":
            changeDebug = True
            break
        elif user_input.lower() == "no":
            changeDebug = False
            break
        
    debugSet = False
    while debugSet != True and changeDebug == True:
        poodleOutput("Please set debug to either true or false >>")
        user_input = raw_input().strip()
        if user_input.lower() == "true":
            debugSet = True
            DEBUG_MODE = True
        elif user_input.lower() == "false":
            debugSet = True
            DEBUG_MODE = False
        
def poodleSearch(term):
	user_inputs = [] #list to hold multiple search terms if available
	if "," in term:
		user_inputs = term.split(",")

	for inputTerm in user_inputs:
		inputTerm = inputTerm.strip()
		poodleSearch(inputTerm)
		
	if not user_inputs:	#BASE CALLER WON'T USE COUNT
		count = 0
		termFoundAt = []
		term = term.lower()
		if term in index:
		    for url in index[term]:
			    count += 1
			    termFoundAt.append(url)
	    
		linkAndRank = []
		for url in termFoundAt:
			linkAndRank.append([[url], pageRanks[url]])

		linkAndRank.sort(key = lambda x:x[1])   #lambda expression to sort by second list element (rank)

		if count == 0:
			poodleOutput("No results found.")
		elif count > 1:
			poodleOutput("[{}] {} results found!\n".format(term, count))
		elif count == 1:
			poodleOutput("[{}] {} result found!\n".format(term, count))
		maxResultCounter = 0
		for x in reversed(linkAndRank):
			maxResultCounter += 1
			if maxResultCounter >= MAX_RESULTS_DISPLAYED:
				break
			print "{} | RANK: {}".format(x[0], x[1])
    
def poodleIndex():
	poodleOutput("Enter -help for POODLE commands (if you don't know what you're doing) >>")
	user_input = raw_input()
	user_input = user_input.strip()
	#Build options (Dictionary/switch structure)
	poodleOpts = {"-build": poodleBuild,
		      "-dump": poodleDump,
		      "-search": poodleSetMaxResults,
                      "-debug": poodleDebug,
		      "-restore": poodleRestore,
		      "-print": poodlePrint,
		      "-ignore": poodleIgnoreList,
		      "-help": poodleHelp,
		      "-exit": sys.exit}

	#POODLE INPUTS - Search & Build options
	if user_input in poodleOpts:
		poodleOpts[user_input]()
	elif user_input[0] == "-":
		poodleOutput("Please enter a valid command!")
	elif len(urlGraph) < 1:
		poodleOutput("You must build or restore a database before entering a search term!")
	else:
		poodleSearch(user_input)
	poodleIndex()

# ----- /POODLE -----#

# ----- MAIN ----- #
poodleSetup()
poodleIndex()

#TODO: Multi-keyword search (poodle)
