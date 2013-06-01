
# Apply Anthony's context filters
def apply_filters(web_results, question, answer_type, limit):
    filters = qa_filters(web_results)
    
    # Initial weigh by rank index
    filters.weigh_index_position()

    # Weigh by question word type that have matching context in results
    q = question.lower()

    if q.startswith('when') or q.startswith('what year') or q.startswith('what month'):
        filters.weigh_temporal_context()
    elif q.startswith('where') or q.startswith('in what country') or q.startswith('in what state') or q.startswith('what country') or q.startswith('what state'):
        filters.weigh_location_context()
    elif q.startswith('how many') or q.startswith('how much') or q.startswith('at what age') or q.startswith('how old'):
        filters.weigh_numerical_context()
        
    # now lets do some features based on answer types
    types = ['LOC', 'HUM', 'NUM', 'ABBR', 'ENTY', 'DESC']
    if answer_type in types:
        filters.addFeaturesByType(answer_type)
    
    return filters.top(limit)

# storing question words
def classify_question(text):
    words = []
    for word in text:
        words.append(word)
    if text.lower().startswith('how'):
        question_word = words[0] + '_' + words[1]
    elif text.lower().startswith('for how'):
        question_word = words[0] + '_' + words[1] + '_' + words[2]
    elif text.lower().startswith('for'):
        question_word = words[0] + '_' + words[1]
    elif text.lower().startswith('from'):
        question_word = words[0] + '_' + words[1]
    else:
        question_word = words[0]
    return question_word

# removing stopwords
def remove_stopwords(text):
    stopwords = nltk.corpus.stopwords.words('english')
    mod_text = ''
    for word in nltk.wordpunct_tokenize(text):
        if word.isalnum():
            if word not in stopwords:
                mod_text += word.lower() + ' '                
    return mod_text.strip()
    
# stemming
def stem_query(mod_text):
    final_text = ''
    stemmer = nltk.PorterStemmer()
    for wordform in mod_text.split(' '):
        stemmed = stemmer.stem(wordform)
        final_text += stemmed + ' '
    return final_text.strip()

def processQuestion(q):
    # methods for finding synonyms/hypernyms/storing data
    wnTags = {'ADJ':'a','ADV':'r','N':'n','V':'v','VD':'v','VG':'v'}
    #tags input question with simplified NLTK tagset
    bagOfWords = nltk.word_tokenize(q)
    #TEST: print 'tokenized'
    taggedWords = nltk.pos_tag(bagOfWords)
    #TEST: print 'tagged words'
    simplified = [(word, simplify_wsj_tag(tag)) for word, tag in taggedWords] 
    #TEST: print taggedWords    
    
    goalWords = {}
    
    #converts NLTK simplified tagset to WordNet-accepted tags
    for word, tag in simplified:
        if wnTags.has_key(tag):
            goalWords[word.lower()] = wnTags[tag]
    
    return goalWords            

def findBestSense(goalWords, q):
    synonyms = []
    commonWords = 0
    count = 0
    maxCount = -1
    optimumSense = ''
    glossWords = []
    senseRank = {}
    
    for key in goalWords.keys():
        #TEST: print 'key =' + str(key)
        POS = str(goalWords[key])
    
        for word in goalWords.keys():
            # for each word in the question:
            senses = wn.synsets(word) # find all the senses for the word
            for sense in senses: # for each sense of the question word
                gloss = sense.definition # retrieve its definition
                for w in gloss:
                    if w not in glossWords:
                        glossWords.append(w)
                    else:
                        continue            
    
        for synset in wn.synsets(key, POS):
            #TEST: print synset
            # for each sense of the head word in the question:
            count = 0
            #TEST: print count
            # pull up the definition of that sense
            goalWordGloss = synset.definition
            for word in goalWordGloss:
                for item in glossWords:
                    if word.lower() == item.lower():
                        count += 1
            senseRank[synset] = count
            
        
        # sorted descending and grab the first (optmium sense)
        sorted_senseRank = sorted(senseRank.iteritems(), key=operator.itemgetter(1), reverse=True)

        synonyms.append(key)    
        
        if len(sorted_senseRank) > 0:
            for lemma in sorted_senseRank[0][0].lemma_names:
                synonyms.append(lemma) 
        
        senseRank.clear()

    return synonyms