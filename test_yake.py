import yake

text="the mermaids are listening to their seashells"
kw_extractor = yake.KeywordExtractor()
language = "en"
max_ngram_size = 2
deduplication_threshold = 0.9
numOfKeywords = 3
custom_kw_extractor = yake.KeywordExtractor(lan=language, n=max_ngram_size, dedupLim=deduplication_threshold, top=numOfKeywords, features=None)
keywords = custom_kw_extractor.extract_keywords(text)
print(keywords)
for kw in keywords:
    print(kw)
if len(keywords)>0:
    print(keywords[0][0])
