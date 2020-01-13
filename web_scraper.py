import requests, re, time
from bs4 import BeautifulSoup
from selenium import webdriver

class WebScraper():
    
    def __init__(self, verbose=True):
        self.stop_sites = [
            'scribd.', 'pinterest.', 'giphy.', 'academia.edu', 'youtube.',
            'udemy.', 'quizlet.', 'doi.org', 'librarything.', 'archiveofourown.org',
            'publishing.cdlib.org', 'vontobel.', 'galegroup.', 'coursera.',
            'english-bangla.', 'oldforum.paradoxplaza.com', 'prezi.',
            'thelectern.blogspot.com', 'onlinelibrary.', 'slideplayer.',
            'springer.', 'jstor.', 'coursehero.', 'slideshare.', 'photobb.net',
            'gamepedia.', 'civilization.wikia', '.pdf', 'forbes.',
            'digitalcommons.', 'studymore.', 'academic.oup.', 'users.sussex.',
            'quizlet', 'ebay', 'thewaythetruthandthelife', 'bookshops',
            'amazon.', 'amazonaws.', 'unionpedia', 'loot.', 'github.',
            'vimeo.', 'books.google'
            ]
        self.stop_extensions = [
            '.pdf', '.PDF', '.txt', '.TXT', '.doc', '.DOC', '.docx', 
            '.DOCX', '.ppt', '.PPT', '.php', '.PHP', '.pps', '.PPS', '.png',
            '.jpg.', '.jpeg', '.gif'
            ]
        self.stop_terms = [
            'download', 'vacation', 'holiday', 'tourism', '(disambiguation)'
            ]
        self.header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        self.verbose = verbose

    def parse_query(self, search_query):
        """
        Parses the seach query by inputting the + signs inbetween tokens,
        preparing the query to be ready for input into google search box
        """
    
        parsed_query = ''
        # Split tokens by space and add + between tham for google search link
        for token in search_query.split():
            parsed_query += '+' + token
        
        # Get rid of the + after the last token
        parsed_query = parsed_query.replace('+', '', 1)
        
        return parsed_query

    #==========================================================================
    # Standard web-search
    #==========================================================================
    def get_google_links_for_single_query(self, parsed_query):
        """Connects to google with specified search query and retrieve results"""
    
        # Get google search source code and run it through BeautifulSoup
        # If requests fails, use selenium and webdriver
        if self.verbose:
            print('#' * 50)
            print('Searching for: "' + str(' '.join(parsed_query.split('+'))) + '"')
        
        google_search = requests.get('https://www.google.com/search?q=' + parsed_query)
        if str(google_search) == '<Response [503]>':
            print('Requests failed to connect to google. Using Selenium')
            browser = webdriver.Chrome('C:\\Users\\tatus\\OneDrive\\NII\\chromedriver.exe')
            browser.get('https://www.google.com/search?q=site%3Aquora.com+' + parsed_query)
            page_source = browser.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            google_links = []
            for links in soup.find_all("a", href = re.compile("(htt.*://www.*)")):
                google_links.append(links['href'])
            google_links = google_links[:-2]
            
        else:
            soup = BeautifulSoup(google_search.content, 'html.parser')
    
            google_links  = []
            index = 1
            # Find all the links which lead to other website as returned by search request
            for links in soup.find_all("a", href = re.compile("(?<=/url\?q=)(htt.*://.*)")):
                link = re.split(":(?=http)", links["href"].replace("/url?q=", ""))
                if len(link) == 1:
                    link = re.sub(r'(&sa=.*)', '', link[0])
                    link = re.sub(r'(%3F)', '?', link)
                    link = re.sub(r'(%3D)', '=', link)
                    link = re.sub(r'%23.*', '', link)
                    if self.verbose:
                        print('Found link #%i : %s' % (index, link))
                    google_links.append(link)
                    index = index + 1
    
        # sleep for a while so not to get blocked by google
        time.sleep(10)
        return list(set(google_links))
    
    def parse_google_links(self, google_links, used_websites):
        
        parsed_google_links = []
        #wikiPageFound = False
        
        for link in google_links:
            if not any(site in link for site in self.stop_sites) \
            and not any(ext in link for ext in self.stop_extensions) \
            and not any(term in link for term in self.stop_terms) \
            and not link in used_websites:
                #if u'wikipedia' in link:
                #    if wikiPageFound is False:
                #        parsed_google_links.append(link)
                #        wikiPageFound = True
                #else:
                parsed_google_links.append(link)
                
        if self.verbose:
            print('After parsing, got ' + str(len(parsed_google_links)) + ' websites from which to retrieve content.\n')
        return parsed_google_links

    def get_content_from_google_links(self, parsed_google_links):
        
        knowledge_sources = []
        webpage_titles = []
        for link in parsed_google_links:
            if 'wikipedia' in link:
                if self.verbose:
                    print('\nGetting content from wikipedia page: %s' % link)
                wiki_article, title = self.get_wiki_article(link)
                knowledge_sources.append(wiki_article)
                webpage_titles.append(title)
                
            elif 'quora' in link:
                if self.verbose:
                    print('\nGetting content from quora page: %s' % link)
                quora_question, quora_answers = self.get_quora_answers(link)
                knowledge_sources.append(quora_answers)
                webpage_titles.append(quora_question)
                    
            elif 'britannica' in link:
                if self.verbose:
                    print('\nGetting content from britannica page: %s' % link)
                britannica_article, title = self.get_britannica_article(link)
                knowledge_sources.append(britannica_article)
                webpage_titles.append(title)
                
            elif 'encyclopedia.com' in link:
                if self.verbose:
                    print('\nGetting content from encyclopedia.com page: %s' % link)
                encyclopedia_article, title = self.get_encyclopedia_article(link)
                knowledge_sources.append(encyclopedia_article)
                webpage_titles.append(title)
                
            elif 'ieg-ego.eu' in link:
                if self.verbose:
                    print('\nGetting content from European History Online page: %s' % link)
                european_history_online_article, title = self.get_european_history_online_article(link)
                knowledge_sources.append(european_history_online_article)
                webpage_titles.append(title)
                
            elif 'newworldencyclopedia.' in link:
                if self.verbose:
                    print('\nGetting content from New World Encyclopedia page: %s' % link)
                new_world_encyclopedia_article, title = self.get_new_world_encyclopedia_article(link)
                knowledge_sources.append(new_world_encyclopedia_article)
                webpage_titles.append(title)
                
            else:
                if self.verbose:
                    print('\nGetting content from a webpage with no designed parsing instruction: %s' % link)
                website_article, title = self.get_website_article(link)
                knowledge_sources.append(website_article)
                webpage_titles.append(title)
                
        return knowledge_sources, webpage_titles
     
    #==========================================================================
    # Quora
    #==========================================================================
    def get_quora_answers(self, quora_link):
        """
        Goes through all the links as returned the getQuoraLinks, connects to each
        website one by one and retrieves the answers to the question.
        
        @TODO: Check the semantic similarity whether the question itself is somewhat
        related to the keywords or intructions. If not, discard it.
        """   
        quora_answers = ''
        quora_question = ''
        # Try connecting to the website and retrieve the question/answers pairs
        try:
            page_source = requests.get(quora_link, headers=self.header)
            soup = BeautifulSoup(page_source.text, 'lxml')
            
            question = soup.find('span', {'class' : 'rendered_qtext'}).contents
            quora_question = str(question[0])
            
            # There might be more than one answer to each question, thus we
            # iterate here through all possible ones and extract them
            answers_unparsed = soup.findAll('span', {'class' : 'ui_qtext_rendered_qtext'})
            for a in answers_unparsed:
                a = re.sub(r'</*.*?>', '', str(a))
                quora_answers += ' ' + a
                
            if self.verbose:
                print('Got asnwers on topic: %s.' % quora_question)
        # Pass if failed meanwhile, probably question is unanswered
        except:
            if self.verbose:
                print('Failed at some point. Probably question has no answers')
            return 'NO ARTICLE FOUND', 'NO TITLE'
            
        time.sleep(5)
        return quora_question, quora_answers

    #==========================================================================
    # Wiki @TODO use API or direct indexing from the wiki dump on history
    #==========================================================================
    def get_wiki_article(self, wiki_link):
        """
        Goes through all the links as returned the getWikiLinks, connects to each
        website one by one and retrieves the wikipedia article on found topics.
        
        @TODO: Check the semantic similarity whether the found wiki topic is relevant
        enough to the topic. Eventually test the semantic similarity on each added
        sentence to judge whether it's neccessary or not? Wiki articles are huge,
        probably with a lot of noise, especially since the examination questions
        require a detailed answer.
        """   
        wiki_article = ''
        # Try connecting to the website and retrieve the question/answers pairs
        try:
            page_source = requests.get(wiki_link, headers=self.header)
            soup = BeautifulSoup(page_source.text, 'html.parser')
            
            title = soup.find('h1', {'class' : 'firstHeading'}).contents
            title = str(title[0])
            
            for unwanted in soup(['sup']):
                unwanted.extract()    # rip it out
            
            wiki_article = soup.findAll('p')
            
            # @TODO: discard if article title is not related to the instructions?
            
            # Parse the article
            wiki_article = re.sub(r'</*.*?>', '', str(wiki_article))
            wiki_article = re.sub(r'\[.*?]', '', wiki_article)
    
            if self.verbose:
                print('Got wiki article on topic: %s.' % title)
        # Pass if failed meanwhile, probably question is unanswered
        except:
            if self.verbose:
                print('Failed retrieving the article, possibly connection to the ' + \
                      'website was not successful.')
            return 'NO ARTICLE FOUND', 'NO TITLE'
            
        time.sleep(5)
        return wiki_article, title

    #==========================================================================
    # Britannica
    #==========================================================================
    def get_britannica_article(self, britannica_link):
        britannica_article = ''
        # Try connecting to the website and retrieve the article
        try:
            page_source = requests.get(britannica_link, headers=self.header)
            soup = BeautifulSoup(page_source.text, 'html.parser')
            
            title = soup.find('title').contents
            title = str(title[0])
            
            for unwanted in soup.findAll('div', {'class' : 'md-modal-body'}):
                unwanted.extract()    # rip it out
            for unwanted in soup.findAll('div', {'class' : 'md-modal-header'}):
                unwanted.extract()    # rip it out
            for unwanted in soup.findAll('div', {'class' : 'md-info-accordion'}):
                unwanted.extract()    # rip it out
            for unwanted in soup.findAll('div', {'class' : 'ui-hidden'}):
                unwanted.extract()    # rip it out  
            for unwanted in soup.findAll('div', {'class' : 'md-learn-more extra-content'}):
                unwanted.extract()    # rip it out
        
            # @TODO: discard if article title is not related to the instructions?
            britannica_article = soup.findAll('p')
            britannica_article = re.sub(r'(</*.*?>)', '', str(britannica_article))
        
            if self.verbose:
                print('Got britannica article on topic: %s.' % title)
        # Pass if failed meanwhile, probably question is unanswered
        except:
            if self.verbose:
                print('Failed retrieving the article, possibly connection to the ' + \
                      'website was not successful.')
            return 'NO ARTICLE FOUND', 'NO TITLE'
            
        time.sleep(5)
        return britannica_article, title

    #==========================================================================
    # Encyclopedia.com
    #==========================================================================
    def get_encyclopedia_article(self, encyclopedia_link):
        encyclopedia_article = ''
        # Try connecting to the website and retrieve the article
        try:
            page_source = requests.get(encyclopedia_link, headers=self.header)
            soup = BeautifulSoup(page_source.text, 'html.parser')
            
            title = soup.find('title').contents
            title = str(title[0])
            
            for unwanted in soup.findAll(['script', 'b', 'h2']):
                unwanted.extract()    # rip it out
            for unwanted in soup.findAll('div', {'class' : 'bylinecontainer'}):
                unwanted.extract()    # rip it out   
        
            # @TODO: discard if article title is not related to the instructions?
            encyclopedia_article = soup.findAll('p')
            encyclopedia_article = re.sub(r'(</*.*?>)', '', str(encyclopedia_article))
            encyclopedia_article = re.sub(r'(\n)', '', encyclopedia_article)
            encyclopedia_article = re.sub(r'See also.*', '', encyclopedia_article)
            
            if self.verbose:
                print('Got encyclopedia.com article on topic: %s.' % title)
        # Pass if failed meanwhile, probably question is unanswered
        except:
            if self.verbose:
                print('Failed retrieving the article, possibly connection to the ' + \
                      'website was not successful.')
            return 'NO ARTICLE FOUND', 'NO TITLE'
            
        time.sleep(5)
        return encyclopedia_article, title

    #==========================================================================
    # European History Online (EGO)
    #==========================================================================
    def get_european_history_online_article(self, european_history_online_link):
        european_history_online_article = ''
        # Try connecting to the website and retrieve the article
        try:
            page_source = requests.get(european_history_online_link, headers=self.header)
            soup = BeautifulSoup(page_source.text, 'html.parser')
            
            title = soup.find('title').contents
            title = str(title[0])
            
            for unwanted in soup.findAll('span', {'class' : 'InsertNoteMarker'}):
                unwanted.extract()    # rip it out
            for unwanted in soup.findAll('div', {'id' : 'header'}):
                unwanted.extract()    # rip it out   
            for unwanted in soup.findAll('p', {'class' : 'author'}):
                unwanted.extract()    # rip it out         
            for unwanted in soup.findAll('div', {'id' : 'article_metadata'}):
                unwanted.extract()    # rip it out   
            for unwanted in soup.findAll('li'):
                unwanted.extract()    # rip it out  
    
            # @TODO: discard if article title is not related to the instructions?
            european_history_online_article = soup.findAll(['p', 'h3'])
            european_history_online_article = re.sub(r'(</*.*?>)', '', str(european_history_online_article))
            european_history_online_article = re.sub(r'Bibliography.*', '', european_history_online_article)
            
            if self.verbose:
                print('Got European History Online article on topic: %s.' % title)
        # Pass if failed meanwhile, probably question is unanswered
        except:
            if self.verbose:
                print('Failed retrieving the article, possibly connection to the ' + \
                      'website was not successful.')
            return 'NO ARTICLE FOUND', 'NO TITLE'
            
        time.sleep(5)
        return european_history_online_article, title

    #==========================================================================
    # New World Encyclopedia
    #==========================================================================
    def get_new_world_encyclopedia_article(self, new_world_encyclopedia_link):
        new_world_encyclopedia_article = ''
        # Try connecting to the website and retrieve the article
        try:
            pageSource = requests.get(new_world_encyclopedia_link, headers=self.header)
            soup = BeautifulSoup(pageSource.text, 'html.parser')
            
            title = soup.find('title').contents
            title = str(title[0])
    
            # @TODO: discard if article title is not related to the instructions?
            new_world_encyclopedia_article = soup.findAll('p')
            new_world_encyclopedia_article = re.sub(r'(</*.*?>)', '', str(new_world_encyclopedia_article))
            new_world_encyclopedia_article = re.sub(r'This article incorporates text from.*', '', 
                                                    new_world_encyclopedia_article)
            
            if self.verbose:
                print('Got New World Encyclopedia article on topic: %s.' % title)
        # Pass if failed meanwhile, probably question is unanswered
        except:
            if self.verbose:
                print('Failed retrieving the article, possibly connection to the ' + \
                      'website was not successful.')
            return 'NO ARTICLE FOUND', 'NO TITLE'
            
        return new_world_encyclopedia_article, title

    #==========================================================================
    # Standard websites
    #==========================================================================
    def get_website_article(self, website_link):
        web_article = ''
        try:
            pageSource = requests.get(website_link, headers=self.header)
            soup = BeautifulSoup(pageSource.text, 'html.parser')
            title = soup.find('title').contents
            title = str(title[0])
            
            # kill all script, style and other elements which usually don't contain
            # the main article. A lot of assumptions go here (mostly that the main
            # website content is usually stored in <p> tag), however that was the 
            # only clear way to parse websites and get the most out of it                                                  
            for unwanted in soup(['script', 'style', 'li', 'ul', 'ol', 'tr', 'td', 'h1', 
                                  'h2', 'h3', 'h4', 'h5', 'h6', 'figcaption', 'dl', 
                                  'td', 'dd', 'nav', 'header', 'footer']):
                unwanted.extract()    # rip it out
            for unwanted in soup.find_all('div', { 'class' : 'caption' }):
                unwanted.extract()
            for unwanted in soup.find_all('div', { 'class' : 'img' }):
                unwanted.extract()
            for unwanted in soup.find_all('div', { 'class' : 'thumbnail'}):
                unwanted.extract()
            for unwanted in soup.find_all('div', { 'class' : 'thumbcaption'}):
                unwanted.extract()
            for unwanted in soup.find_all('div', { 'class' : 'header' }):
                unwanted.extract()
            for unwanted in soup.find_all('div', { 'class' : 'footer' }):
                unwanted.extract()
            for unwanted in soup.find_all('div', { 'class' : 'menu' }):
                unwanted.extract()
            for unwanted in soup.find_all('div', { 'class' : 'nav' }):
                unwanted.extract()
            for unwanted in soup.find_all('div', { 'class' : 'bibliography' }):
                unwanted.extract()
            for unwanted in soup.find_all('div', { 'class' : 'references' }):
                unwanted.extract()
                
            web_article = str(soup.findAll('p'))
            web_article = re.sub(r'(</*.*?>)', '', web_article)
            web_article = re.sub(r'(\n)', ' ', web_article)
            web_article = re.sub(r'(\t)', '', web_article)
            web_article = re.sub(r'Bibliography.*', '', web_article)
            web_article = web_article.strip()
            
            if self.verbose:
                print('Got the article with the following title from website: %s' % title)
        # Pass if failed meanwhile, probably question is unanswered
        except:
            if self.verbose:
                print('Couldn\'t parse the website, probably the connection was unsuccessful.')
            return 'NO ARTICLE FOUND', 'NO TITLE'
        
        return web_article, title