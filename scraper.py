import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import hashlib
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

simhash_vals = []


def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]


def correct_path(url):
    path = [r".ics.uci.edu/", r".cs.uci.edu/", r".informatics.uci.edu/", r".stat.uci.edu/",
            r"today.uci.edu/department/information_computer_sciences/"]
    for p in path:
        if url.find(p) != -1:
            return True
    return False


def simhash(soup):  # calculate sim hash of current page based on soup
    contents = ''
    for i in soup:  # combine contents of all tags in soup into one string
        contents += i.content
        contents += ' '
    tokens = word_tokenize(contents)  # tokenize words in contents
    stopWords = set(stopwords.words('english'))     # download list of stopwords
    for i in tokens:    # remove stopwords from list of tokens
        if i in stopWords:
            tokens.remove(i)
    freqs = computeWordFrequencies(tokens)  # calculate frequencies of tokens
    words = list(freqs.keys())          # extract words(keys) from freqs
    weights = list(freqs.values())      # extract values from freqs to use as weights
    for i in range(0, len(words)):      # hash each word using md5
        words[i] = hashlib.md5(i.encode())

    # initialize vector to and update its components based on the weights in freqs[]
    # generate fingerprint based on vector
    # store fingerprint in simhash_vals


def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: status code returned by the server. 200 is OK, you got the page.
    #               Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content

    # check for some basic info, is this valid or not, do we have a content or not
    links_grabbed = []

    if not is_valid(resp.url) or resp.status != 200 or not resp.raw_response.content:
        return links_grabbed

    try:
        str_content = resp.raw_response.content.decode("utf-8", errors="?")  # decode using utf-8
    except:
        print("Error ", resp.raw_response.url)
        return links_grabbed

    soup = BeautifulSoup(str_content)
    for tag in soup.findAll('a', href=True):
        curr_url = tag['href']
        if curr_url.startswith('/') and not curr_url.startswith(
                "//"):  # if it expects us to append the domain to the link
            if "today.uci.edu/department/information_computer_sciences/" in url:
                domain = url[:url.index("today.uci.edu/department/information_computer_sciences") + 54]
                curr_url = domain + curr_url
            else:
                domain = url[:url.index(".uci.edu") + 8]
                curr_url = domain + curr_url
        if "#" in curr_url:
            fragmentStart = curr_url.index("#")  # finds the fragments and gets rid of them
            curr_url = curr_url[:fragmentStart]
        if is_valid(curr_url) and correct_path(curr_url) and curr_url not in links_grabbed:
            links_grabbed.append(curr_url)
    print(f"number of url: {len(links_grabbed)}")
    return links_grabbed


'''
old fashion way, work, but still have some issue
'''


# result = []
# while True:
#     if cur_index == size-1:               # break if iterator points to end of content
#         break
#     index = str_content.find('http', cur_index)    # starting from iterator position, find 'http'
#     if index == -1:                     # break if 'http' doesn't exist in remainder of content
#         break

#     curr_str_list = []
#     while index < size and str_content[index] not in [" ","\n", "\"","'"]: #check for the end of url string
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
        # traps checking
        # url.endswith("Avscode.jpg&ns=") or url.endswith("Avscode.jpg") or url.endswith("3Ajupyterhub")
        if url.startswith("https://wics.ics.uci.edu/events/20") or url.endswith("?share=facebook") or url.endswith(
                "?share=twitter") or url.endswith("?action=login") \
                or url.endswith(".zip") or url.endswith(".pdf") or url.endswith("txt") or url.endswith(
            "tar.gz") or url.endswith(".bib") or url.endswith(".htm"):
            return False
        elif ("wics" in url and "/?afg" in url and not (url.endswith("page_id=1"))) or (
                "wics" in url and "/img_" in url):
            return False
        elif "doku.php" in url:  # trying to make parsing this particular website and its traps faster
            if "?" in url:
                return False
        elif "grape.ics.uci.edu" in url and ("action=diff&version=" in url or "timeline?from" in url):
            return False  # maybe not a trap, but is low information, do we crawl?
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
        print("TypeError for ", parsed)
        raise


# Assignment 1 PartA computeWordFrequencies
def computeWordFrequencies(tokens):
    results = {}
    while len(tokens) > 0:
        count = 0
        token = tokens[0]
        while len(tokens) > 0 and tokens[0] == token:
            count += 1
            tokens.remove(token)
        results.update({token: count})

    return results
