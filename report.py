


class Report:
    def __init__(self):
        self.simhash_vals = []
        self.longest_page_val = 0
        self.longest_page_url = ''
        self.fingerPrint_size = 200
        self.unique_pages = 0
        self.token_freq = {}
        self.similar_threshold = 0.00
        self.min_word_threshold = 200
        self.subdomain_count = {}

    def printReport(self):
        print(f"Most content url: {self.longest_page_url} with number of token(stop word) {self.longest_page_val}")
        print(f"Number of unique pages {self.unique_pages}")
        #sorting big token_freq, get top 50
        sorted_freqs = sorted(self.token_freq.items(), key=lambda x:x[1],reverse=True)
        print(f"Freq dic {sorted_freqs[:50]}")
        listofsubdomains = [list(subitem) for subitem in self.subdomain_count.items()]
        listofsubdomains = sorted(listofsubdomains, key=lambda i:i[0])
        print(f"list of subdomains and their count: {listofsubdomains}")