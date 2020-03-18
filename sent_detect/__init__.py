import logging
import azure.functions as func

import json
import re
import pathlib


from sklearn.datasets import load_files
import pandas as pd
import os, os.path

#Prepare NLP
import spacy

# Prepare Stop Words DataSet
import nltk
from nltk.corpus import stopwords


import gensim

nlp=None
trigram_mod=None  
dictionary=None
lda_model_paragraph=None
bigram_mod=None
stop_words=None
tempFilePath=None  

def sent_to_words(sentences):    
    for sentence in sentences:        
        yield(gensim.utils.simple_preprocess(str(sentence), deacc=True))  


# Build the bigram and trigram models
#bigram = gensim.models.Phrases(data_words, min_count=5, threshold=150) 
# higher threshold fewer phrases.
#trigram = gensim.models.Phrases(bigram[data_words], threshold=150)
# Faster way to get a sentence clubbed as a trigram/bigram
#bigram_mod = gensim.models.phrases.Phraser(bigram)
#trigram_mod = gensim.models.phrases.Phraser(trigram)

# Define functions for stopwords, bigrams, trigrams and lemmatization
def remove_stopwords(texts, stop_words):    
    return [[word for word in gensim.utils.simple_preprocess(str(doc)) if word not in stop_words] for doc in texts]
def make_bigrams(texts, bigram_mod):    
    return [bigram_mod[doc] for doc in texts]
def make_trigrams(texts,bigram_mod,trigram_mod):    
    return [trigram_mod[bigram_mod[doc]] for doc in texts]
#def lemmatization(texts, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV']):  
#def lemmatization(texts, allowed_postags=['NOUN', 'VERB']): 

def lemmatization(nlp, texts, allowed_postags=['NOUN', 'ADJ', 'VERB']):    
    texts_out = []    
    for sent in texts:        
        doc = nlp(" ".join(sent))        
        texts_out.append([token.lemma_ for token in doc if token.pos_ in allowed_postags])    
    return texts_out

#g_filesmsg=""
def prepare_environment():
    global nlp, trigram_mod,dictionary,lda_model_paragraph,stop_words,bigram_mod,tempFilePath #,g_filesmsg
    import time

    rootfolder=pathlib.Path(__file__).parent
    logging.info("Root Folder is {}".format(rootfolder))

    #list uploaded files
    mypath=rootfolder
    listOfFiles=[]
    for (dirpath, dirnames, filenames) in os.walk(mypath):
        listOfFiles += [os.path.join(dirpath, file) for file in filenames]
    logging.info("Files & Folders are {}".format(listOfFiles))

    spacy.util.set_data_path(rootfolder)
    start_time = time.time()
    logging.info("Parpare Env")
    logging.info("--- %s seconds ---" % (time.time() - start_time))
    start_time = time.time()
    #if not spacy.util.is_package("en_core_web_sm"):
        #spacy.cli.download('en_core_web_sm','--data-path /en_core_web_sm2/')
    logging.info("Download web sm")
    logging.info("--- %s seconds ---" % (time.time() - start_time))
    start_time = time.time()
    if not stop_words:
        nltk.download('stopwords')
        print("Download Stopword")
        print("--- %s seconds ---" % (time.time() - start_time))
        start_time = time.time()
        stop_words = stopwords.words('english')
        stop_words.extend(['may'])
    logging.info("Ininit Stop Word")
    logging.info("--- %s seconds ---" % (time.time() - start_time))
    start_time = time.time()
    if not bigram_mod:
        modepath=rootfolder.joinpath('models','bigram_model.pkl')
        bigram_mod = gensim.models.Phrases.load(str(modepath))
    logging.info("Load Bigram")
    logging.info("--- %s seconds ---" % (time.time() - start_time))
    start_time = time.time()
    if not trigram_mod:
        modepath=rootfolder.joinpath('models','trigram_model.pkl')
        trigram_mod = gensim.models.Phrases.load(str(modepath))
    if not dictionary:
        modepath=rootfolder.joinpath('models','dictionary.gensim')
        dictionary=gensim.corpora.Dictionary.load(str(modepath))
    if not lda_model_paragraph:
        modepath=rootfolder.joinpath('models','doc_topic_model01.gensim')
        lda_model_paragraph= gensim.models.ldamodel.LdaModel.load(str(modepath))
    logging.info("--- %s seconds ---" % (time.time() - start_time))
    start_time = time.time()

    if not nlp:
        #spacy.cli.download('en_core_web_sm','--data-path /en_core_web_sm2/')
        logging.info("Start Downlod en_core for test")
        spacy.cli.download('en_core_web_sm')
        logging.info("End Downlod en_core for test")
        nlp = spacy.load("en_core_web_sm", disable=['parser', 'ner'])
        #nlp = en_core_web_sm.load()
    logging.info("Loaded Spacy")
    logging.info("--- %s seconds ---" % (time.time() - start_time))
    return nlp,stop_words,bigram_mod,trigram_mod,dictionary,lda_model_paragraph



def prepare_text_for_lda(text,nlp,stop_words,bigram_mod,trigram_mod):
    data = [text]
    data_words = list(sent_to_words(data))
    data_words_nostops = remove_stopwords(data_words,stop_words)
    data_words_bigrams = make_bigrams(data_words_nostops,bigram_mod)
    data_lemmatized = lemmatization(nlp,data_words_bigrams, allowed_postags=['NOUN', 'ADJ', 'VERB'])
    lda_texts = data_lemmatized
    return lda_texts


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    logging.info(f"Headers: {req.headers}")
    logging.info(f"Params: {req.params}")
    logging.info(f"Route Params: {req.route_params}")
    logging.info(f"Body: {req.get_body()}")

    output = {"values": []}
    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
            output=run(req_body)
        except ValueError:
            pass
        else:
            name = req_body.get('name')


    if name:
        return func.HttpResponse(f"Hello {name}!")
    else:
        return func.HttpResponse(json.dumps(output), mimetype='application/json')
        #return func.HttpResponse(
        #     "Please pass a name on the query string or in the request body",
        #     status_code=400
        #)

def get_topics(content,nlp,stop_words,bigram_mod,trigram_mod,dictionary,lda_model_paragraph):
    new_doc = prepare_text_for_lda(content,nlp,stop_words,bigram_mod,trigram_mod)
    new_doc_bow = dictionary.doc2bow(new_doc[0])
    all_topics = lda_model_paragraph.get_document_topics(new_doc_bow)
    top_topic = sorted(all_topics, key=lambda topic: topic[1], reverse=True)[0][0]

    wp = lda_model_paragraph.show_topic(top_topic)
    topic_keywords = ", ".join([word for word, prop in wp])
    return top_topic,topic_keywords

def run(json_data):
    try:
        #raw_data = json.loads(raw_data)
        raw_data = json_data
        output = {"values": []}
        for doc in raw_data["values"]:
            record_id = doc.get('recordId')
            doc_data = doc.get("data")
            record_output = {
                'recordId': record_id,
                'data': {},
            }
            if doc_data is None:
                record_output['errors'] = [{ "message": "data not found"}]
                output['values'].append(record_output)
                continue
            doc_text = doc_data.get("text", "not found")
            if doc_text is "not found":
                record_output['errors'] = [{ "message": "text field not found"}]
            elif type(doc_text) is not str:
                record_output['warnings'] = [{ "message": "No genetic codes found in text field"}]
            else:

                nlp,stop_words,bigram_mod,trigram_mod,dictionary,lda_model_paragraph=prepare_environment()

                # Disable for testing Functions
                topic_id, topics=get_topics(doc_text,nlp,stop_words,bigram_mod,trigram_mod,dictionary,lda_model_paragraph)
                codes=topic_id
                #record_output['data']['topic_id'] = codes
                #record_output['data']['topic_content'] = topics

                #record_output['data']['topic_id'] = 0
                #record_output['data']['topic_content'] = "Test1, Test2"+g_filesmsg
                
                alltopics=['Solution','Team Resources','Proposal','Support and Training','Vendor','Supplier','Ref Case','Project Transfer','Time','DXC Services','Datum','User Requirements','Aplication Approach','Report','Customer Reuqirements','Server Software','Health Care','Change Management','Service Level','Call Center']

                record_output['data']['topic_id'] = codes
                record_output['data']['topic_content'] = topics.replace(' ','').split(',')
                record_output['data']['topic']=alltopics[codes]

            output['values'].append(record_output)
        return output
    except Exception as e:
        result = str(e)
        return {"error": result}
