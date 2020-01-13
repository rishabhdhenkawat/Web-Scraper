# Web-Scraper

Works sligthly different than most other ones I suppose. 

The module connects to google with a search query and retrieves all the links from the first page. 
Then, it connects to every link one by one and retrieves the the textual content from each.

## Stop sites / extensions

Since the aim is to retrieve only textual content, some websites like youtube, facebook, pintrest etc are automatically discarded 
before extracting content. Same goes for various special extensions like .pdf, .doc or .jpg, simply because it's either wrong format
or it would take too long to parse the whole book.

## Libraries

The whole thing is build using BeautifulSoup and regex expressions for parsing content out of website source code and requests for
connecting to the websites. Since it's a bot, there exists a possibility that google would ban the connection - in that case the scraper
tries connecting to google using selenium - keep in mind, you need chromedriver to use it and also that would open a developer 
chrome browser to extract the links.

## Usage

```
from web_scraper import WebScraper

# Used websites as for running a scraper in loop with various simialr keywords - so the content won't be repeated
used_websites = []
ws = WebScraper(versbose=True)

# Query which will be used as an input to google search
search_query = 'I like pancakes'
parsed_query = ws.parse_quert(search_query)

# Gets links and parses them, removing stopsites and stop extensions
google_links = ws.get_google_links_for_single_query(parsed_query)
parsed_google_links = ws.parse_google_links(google_links, used_websites)

# Extracts the content from every link retrieved
google_links_content, website_titles = ws.get_content_from_google_links(parsed_google_links)
assert len(google_links_content) == len(website_titles) == len(parsed_google_links)

print('Extracted the textual content from {} websites on the query topic.'.format(len(website_titles)))
used_websites += parsed_google_links
```
