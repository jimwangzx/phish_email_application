# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import joblib
import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
from itertools import chain
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score, f1_score
from sklearn.naive_bayes import BernoulliNB, MultinomialNB
from sklearn.preprocessing import OneHotEncoder
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from scipy.sparse import coo_matrix
stopwords = set(stopwords.words("english"))
ps = PorterStemmer()


# %%
from joblib import dump, load
# bernomodel = load("bernomodel.joblib")
multimodel = load("multimodel.joblib")
# norm_multimodel = load("normalizedmultimodel.joblib")


# %%
import nltk
nltk.download ('punkt')
nltk.download('stopwords')


# %%
def write_predictions(file_name, pred):
    df = pd.DataFrame(zip(range(len(pred)), pred))
    df.columns = ["id", "label"]
    df.to_csv(file_name, index=False)


# %%
def tokenize(text):
    if not text:
        print('The text to be tokenized is a None type. Defaulting to blank string.')
        text = ''
    return nltk.word_tokenize(str(text))


# %%
def stem(tokens):
    return [ps.stem(token) for token in tokens]
#     return tokens


# %%
def n_gram(tokens, n=1):
    """
    :param tokens: a list of tokens, type: list
    :param n: the corresponding n-gram, type: int
    return a list of n-gram tokens, type: list
    e.g.
    Input: ['text', 'mine', 'is', 'to', 'identifi', 'use', 'inform', '.'], 2
    Output: ['text mine', 'mine is', 'is to', 'to identifi', 'identifi use', 'use inform', 'inform .']
    """
    if n == 1:
        return tokens
    else:
        results = list()
        for i in range(len(tokens)-n+1):
            results.append(" ".join(tokens[i:i+n]))
        return results


# %%
def filter_stopwords(tokens):
    """
    :param tokens: a list of tokens, type: list
    return a list of filtered tokens, type: list
    e.g.
    Input: ['text', 'mine', 'is', 'to', 'identifi', 'use', 'inform', '.']
    Output: ['text', 'mine', 'identifi', 'use', 'inform', '.']
    """

    return [token for token in tokens if token not in stopwords and not token.isnumeric()]


# %%
def get_onehot_vector(feats, feats_dict):
    """
    :param feats: a list of features, type: list
    :param feats_dict: a dict from features to indices, type: dict
    return a feature vector,
    """

    vector = np.zeros(len(feats_dict), dtype=np.float)
    for f in feats:
        f_idx = feats_dict.get(f, -1)
        if f_idx != -1:
            vector[f_idx] = 1
    return vector





# # %%
# test_feats = list()
# for i in range(len(test_ids)):
#     # concatenate the stemmed token list and all n-gram list together
#     test_feats.append(test_stemmed[i]+test_2_gram[i]+ test_3_gram[i] + test_4_gram[i])

# test_feats_matrix = coo_matrix(np.vstack([get_onehot_vector(f, feats_dict) for f in test_feats]))


# # %%
# test_pred = bernomodel.predict(test_feats_matrix.toarray())
# test_score = accuracy_score(test_labels.values, test_pred)
# print("test accuracy", test_score)


# %%
def prepareEmailFreq(text):
    email_tokens = tokenize(text)
    email_tokens = filter_stopwords(email_tokens)
    email_stem = stem(email_tokens)
    # n-gram
    email_2gram = n_gram(email_stem, 2) 
    email_3gram = n_gram(email_stem, 3) 
    email_4gram = n_gram(email_stem, 4) 
    email_feats_Count = Counter()
        
    email_feats_Count.update(email_stem)
    
    email_feats_Count.update(email_2gram)
    
    email_feats_Count.update(email_3gram)
    
    email_feats_Count.update(email_4gram)
    
    return email_feats_Count

def combinefectCount(maincount, emailcount):
    for feat in emailcount:
        if maincount.get(feat):
            maincount[feat] = maincount[feat]+emailcount[feat]
        else:
            maincount[feat] = emailcount[feat]

def set_feat_list_counter(dataset):
    """
    set_feat_list_counter(dataset)
    :param dataset: iterable of text
    return feature counter of the whole dataset and list of feature counter of each text
    """
    set_feat_counter = Counter()
    ele_feat_counter_list = []
    for text in dataset:
        em_count = prepareEmailFreq(text)
        ele_feat_counter_list.append(em_count)
        combinefectCount(set_feat_counter, em_count)
    return (set_feat_counter, ele_feat_counter_list)

def multihot(set_feat_list, ele_feat_counter_list, normalize = True):
    """
    multihot(set_feat_set, set_em_count)
    :param set_feat_list: list of feature(text)
    :param ele_feat_counter_list: list of counter of feature of each set element
    return normalized (sum = 1) multihot 2D ndarray of each element regards to the feat_list
    """
    multihot = np.ndarray([len(ele_feat_counter_list),len(set_feat_list)])
    for idx in range(len(ele_feat_counter_list)): #email index
        ele_count = ele_feat_counter_list[idx]
        for featIdx in range(len(set_feat_list)): #feature from feature list
            if ele_count.get(set_feat_list[featIdx]):
                multihot[idx][featIdx] = ele_count.get(set_feat_list[featIdx])
            else:
                multihot[idx][featIdx] = 0
        if multihot[idx].sum() and normalize:
            multihot[idx]/=multihot[idx].sum()
    return multihot


# %%
import json

with open("multi_feats_dict.json", "r") as input:
    trainfeatlist = json.load(input)


# # %%
# testfeatcounter, test_em_feat_counter_list = set_feat_list_counter(test['Content'])
# test_multihot = multihot(trainfeatlist, test_em_feat_counter_list, normalize = False)

# multi_test_pred = multimodel.predict(test_multihot)
# multi_test_score = accuracy_score(test_labels.values, multi_test_pred)
# print("test accuracy", multi_test_score)


def predict(email):
    testfeatcounter, test_em_feat_counter_list = set_feat_list_counter([email])
    test_multihot = multihot(trainfeatlist, test_em_feat_counter_list, normalize = False)

    multi_test_pred = multimodel.predict(test_multihot)
    return multi_test_pred


# # %%
# norm_testfeatcounter, norm_test_em_feat_counter_list = set_feat_list_counter(test['Content'])
# norm_test_multihot = multihot(trainfeatlist, norm_test_em_feat_counter_list, normalize = True)

# norm_multi_test_pred = norm_multimodel.predict(norm_test_multihot)
# norm_multi_test_score = accuracy_score(test_labels.values, norm_multi_test_pred)
# print("test accuracy", norm_multi_test_score)


# %%
# fig, ax = plt.subplots()
# plt.ylim(0.7,0.9)
# plt.bar("""Bernoulli
# Naive Bayes""", test_score)
# plt.bar("""General
# Multinomial
# Naive Bayes""", multi_test_score)
# plt.bar("""Normalized
# Multinomial
# Naive Bayes""", norm_multi_test_score)
# plt.title("Evaluate  different models")
# plt.ylabel("Accuracy")
# plt.rc('font', size=10)
# ax.spines['right'].set_visible(0)
# ax.spines['top'].set_visible(0)
# plt.savefig("Evaluate different models.png", dpi = 200, bbox_inches = "tight")
# plt.show()


