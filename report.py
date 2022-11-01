


class Report:
    def __init__(self):
        self.simhash_vals = []
        self.longest_page_val = 0
        self.longest_page_url = ''
        self.fingerPrint_size = 200
        self.unique_pages = 0
        self.token_freq = {}
        self.similar_threshold = 0.0
        self.min_word_threshold = 100

    def printReport(self):
        print(f"Most content url: {self.longest_page_url} with number of token(stop word) {self.longest_page_val}")
        print(f"Number of unique pages {self.unique_pages}")
        #sorting big token_freq, get top 50
        sorted_freqs = sorted(self.token_freq.items(), key=lambda x:x[1],reverse=True)
        print(f"Freq dic {sorted_freqs[:50]}")