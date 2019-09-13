# Test data

Test data was downloaded from NLTK on 9/12/19:
```
import nltk
nltk.download("movie_reviews")
reviews = [{"fileid": fileid, "text": nltk.corpus.movie_reviews.raw(fileid)} for fileid in nltk.corpus.movie_reviews.fileids()]
reviews = pd.DataFrame(reviews)
reviews.to_csv("test_data.csv", encoding="utf8")
```