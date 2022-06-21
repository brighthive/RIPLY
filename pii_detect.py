
# from nltk.tag.stanford import StanfordNERTagger
# from nltk.tokenize import word_tokenize

import re
import pandas as pd
class detection(object):
    def __init__(self):
        # self.standford_ner = StanfordNERTagger('./classifiers/english.all.3class.distsim.crf.ser.gz')
        pass

    def analyze(self,array):
        self.array=array
        phone_regex=re.compile("^\s*(?:\+?(\d{1,3}))?[-. (]*(\d{3})[-. )]*(\d{3})[-. ]*(\d{4})(?: *x(\d+))?\s*$",re.IGNORECASE)
        street_regex=re.compile("^(\\d{1,}) [a-zA-Z0-9\\s]+(\\,)?$",re.IGNORECASE)
        city_regex=re.compile("^[a-zA-Z]+(\\,)?$",re.IGNORECASE)
        zipcode_regex=re.compile("^[0-9]{5,6}$",re.IGNORECASE)
        state_regex=re.compile("^[A-Z]{2}",re.IGNORECASE)
        whole_street_regex=re.compile("^(\\d{1,}) [a-zA-Z0-9\\s]+(\\,)? [a-zA-Z]+(\\,)? [A-Z]{2} [0-9]{5,6}$",re.IGNORECASE)
        # array_join=",".join([str(value) for value in self.array])
        # tokenize_text=word_tokenize(array_join)

        # birthday_regex=re.comp             # birthday regext don't know weather needed
        # tokenize_text_clean=[]
        # for i in tokenize_text:
        #     if i != " " and i !=",":
        #         tokenize_text_clean.append(i)

        # classified_text=self.standford_ner.tag(tokenize_text_clean)

        # tags=[self.standford_ner.tag(token_val) for token_val in tokenize_text]
        # print(classified_text)
        array_score=[]
        ### First go through Common regex
        for value in self.array:
           street_value= street_regex.match(str(value))
           phone_value=phone_regex.match(str(value))
           city_value=city_regex.match(str(value))
           zipcode_value=zipcode_regex.match(str(value))
           state_value=state_regex.match(str(value))
           whole_street_value=whole_street_regex.match(str(value))

           if state_value!=None or phone_value!=None or city_value!=None or zipcode_value!=None or street_value!=None or whole_street_value!=None:
               array_score.append(1)
           else:
               array_score.append(0)
        return sum(array_score) / len(array_score)
       

