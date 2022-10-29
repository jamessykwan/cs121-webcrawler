import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup


def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def correct_path(url):
    path = [r".ics.uci.edu/", r".cs.uci.edu/" ,r".informatics.uci.edu/" ,r".stat.uci.edu/" ,r"today.uci.edu/department/information_computer_sciences/"]
    for p in path:
        if url.find(p) != -1:
            return True
    return False

def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content


    #check for some basic info, is this valid or not, do we have a content or not
    links_grabbed = []

    if not is_valid(resp.url) or resp.status != 200 or  not resp.raw_response.content:
        return links_grabbed

    
    str_content =[]
    try:
        str_content = resp.raw_response.content.decode("utf-8",errors="?") #decode using utf-8
    except:
        print("Error ",resp.raw_response.url)
        return links_grabbed
    
    soup = BeautifulSoup(str_content)
    for tag in soup.findAll('a', href=True):
        url = tag['href']
        if "#" in url:
            fragmentStart = url.index("#") #finds the fragments and gets rid of them
            url = url[:fragmentStart]
        if is_valid(url) and correct_path(url) and url not in links_grabbed: 
            links_grabbed.append(url)
    print(f"number of url: {len(links_grabbed)}")
    return links_grabbed
    
'''
REGEX method, bad, a lot of error
'''
    #regex = "href=\"(.*?)\""
    #print("number of char:", len(str_content))
    # results = re.findall(regex,str_content)
    # links_grabbed = []
    # size = len(str_content) #size of the page, aka number of the byte
    # cur_index = 0 #using a index to read character by character

    # for result in results:
    #     print(result)
    #     result = result.replace("\\","")
    #     if is_valid(result) and result not in links_grabbed:
    #         links_grabbed.append(result)


'''
old fashion way, work, but still have some issue
'''
    #result = []
    # while True:
    #     if cur_index == size-1:               # break if iterator points to end of content
    #         break
    #     index = str_content.find('http', cur_index)    # starting from iterator position, find 'http'
    #     if index == -1:                     # break if 'http' doesn't exist in remainder of content
    #         break

    #     curr_str_list = []
    #     while index < size and str_content[index] not in [" ","\n", "\"","'"]: #check for the end of url string, s.t "http:xxx "
    #         if not str_content[index] == "\\":
    #             curr_str_list.append(str_content[index])
    #         index += 1
    #     curr_str = "".join(curr_str_list)
    #     cur_index += len(curr_str)

    #     if is_valid(curr_str) and curr_str not in result: #make sure this url is not duplicated and is valid
    #         result.append(curr_str)
    # return result

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise
