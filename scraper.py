import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import hashlib
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import numpy as np

# simhash_vals = {'.ics.uci.edu/': [], '.cs.uci.edu/': [], '.informatics.uci.edu/': [], '.stat.uci.edu/': [], 
#                'today.uci.edu/department/information_computer_sciences/': []}
simhash_vals = []
longest_page_val = 0
longest_page_url = ''
fingerPrint_size = 200

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


def similar(finger1,finger2,threshold=1.0):
    assert len(finger1) == len(finger2), f"size doesn't match {len(finger1)},{len(finger2)}"
    n = len(finger1)
    count = sum([1 if finger1[i] == finger2[i] else 0 for i in range(n)])
    return count/n >= 1


def simhash(url, soup):                                  # calculate sim hash of current page based on soup
    global longest_page_val                         # track max number of words in a page using global vars
    global longest_page_url
    global fingerPrint_size
    if len(soup) == 0:                              # return if soup empty
        return

    contents = soup.get_text()
    tokens = word_tokenize(contents)                # tokenize words in contents
    stop_words = set(stopwords.words('english'))    # download list of stopwords
    filtered_tokens = [word for word in tokens if word not in stop_words]
 
    freqs = nltk.FreqDist(filtered_tokens)
    sorted_freqs = sorted(freqs.items(), key=lambda x:x[1],reverse=True) #sort the disk by highest to lowest
    words = [a for a,b in sorted_freqs]                      # extract words(keys) from freqs
    weights = [b for a,b in sorted_freqs]                  # extract values from freqs to use as weights

    weight_sum = sum(weights)                                  # compute total number of words in page

    
    if weight_sum > longest_page_val:
        longest_page_val = weight_sum
        longest_page_url = url

    binary_word = []
    for i in range(len(words)):                  # hash each word using md5
        temp = hashlib.md5(words[i].encode())       # encode word
        temp = temp.hexdigest()                     # convert to hex
        bin_str = bin(int(temp, 16))[2:] #get rid of '0b'
        binary_word.append(bin_str.zfill(fingerPrint_size))      # convert to binary


    fingerprint = [0]*fingerPrint_size
    for i in range(0, len(fingerprint)):               # update vector components based on words & weights
        for j in range(0, len(words)):
            try:
                fingerprint[i] = fingerprint[i] + weights[j] if int(binary_word[j][i]) == 1 else fingerprint[i] - weights[j]
            except:
                print(words[j])
    for i in range(0, len(fingerprint)):            # generate final fingerprint
        fingerprint[i] = 1 if fingerprint[i]>0 else 0
    return fingerprint


def extract_next_links(url, resp):
    global simhash_vals
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
    fingerprint = simhash(url, soup)             # call simhash function to generate fingerprint of current page

    # if fingerprint in simhash_vals:       # if fingerprint already in simhash_vals, is an exact duplicate
    #     return links_grabbed
    for vals in simhash_vals:
        if similar(fingerprint,vals,1.0):
            return links_grabbed
    simhash_vals.append(fingerprint)
                                           # compare fingerprint against all other fingerprints in simhash_vals
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
    print(f"number of url: {len(links_grabbed)} number of fingerprint {len(simhash_vals)}")
    return links_grabbed




def is_valid(url):
    # Decide whether to crawl this url or not.
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        #traps checking
        # url.endswith("Avscode.jpg&ns=") or url.endswith("Avscode.jpg") or url.endswith("3Ajupyterhub")
        if url.startswith("https://wics.ics.uci.edu/events/20") or url.endswith("?share=facebook") or url.endswith("?share=twitter") or url.endswith("?action=login")\
        or url.endswith(".zip") or url.endswith(".pdf")or url.endswith("txt") or url.endswith("tar.gz") or url.endswith(".bib") or url.endswith(".htm") or url.endswith(".xml") or url.endswith(".java"):
            return False
        elif ("wics" in url and "/?afg" in url and not (url.endswith("page_id=1"))) or ("wics" in url and "/img_" in url):
            return False
        elif "doku.php" in url: #trying to make parsing this particular website and its traps faster
            if "?" in url:
                return False
        elif "grape.ics.uci.edu" in url and ("action=diff&version=" in url or "timeline?from" in url or ("?version=" in url and ur.endswith("?version=1"))):
            return False #not trap but low info skipped
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
