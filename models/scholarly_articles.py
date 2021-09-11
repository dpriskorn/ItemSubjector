from models.wikidata import Labels


class ScholarlyArticleLabels(Labels):
    """This class has all code needed to fetch scientific articles, extract the labels,
    clean them and find the top n-grams we need"""

    def get_ngrams(self):
        self.fetch_labels_into_dataframe(quantity=1000,
                                         # Fetch scientific articles without main subject
                                         query="haswbstatement:P31=Q13442814 -haswbstatement:P921")
        return self.extract_top_100_ngrams()