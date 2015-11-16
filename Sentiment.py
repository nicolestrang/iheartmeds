#!/bin/usr/python
"""
Created on Sat Jul 25 18:38:55 2015

@author: nicolestrang
"""
import re
from nltk.corpus import stopwords
import pandas as pd
import nltk.classify.util
from nltk.classify import NaiveBayesClassifier
from random import shuffle


def tokenize(text):
    '''Splits a text to words, separates by space and punctuation, 
    converts to lowercase.'''
    return re.findall(r"[\w']+|[.,!?;-]", text)

# Get words from comment 
def word_feats(words):
    stopset = list(set(stopwords.words('english')))
    return dict([(word, True) for word in tokenize(words) if word not in stopset])

def prep_data(df,train_pct):
       # Get positve and negative reviews in lists
    pos_revs = df["Comments"][df["Value"]=='pos'].tolist()
    neg_revs = df["Comments"][df["Value"]=='neg'].tolist()

    # Remove stop words and tag words in positive comments as postive
    pos_feats = [(word_feats(f), 'pos') for f in pos_revs ]
    shuffle(pos_feats)

    # Remove stop words and tag words in negative comments as negative
    neg_feats = [(word_feats(f), 'neg') for f in neg_revs ]
    shuffle(neg_feats)

    # Split data so 80% for training and 20% for testing
    negcutoff = int(len(neg_feats)*train_pct)
    poscutoff = int(len(pos_feats)*train_pct)
 
    trainfeats = neg_feats[:negcutoff] + pos_feats[:poscutoff]
    testfeats = neg_feats[negcutoff:] + pos_feats[poscutoff:]
    print 'train on %d instances, test on %d instances' % (len(trainfeats), len(testfeats))
    
    return trainfeats, testfeats

def classifier_stats(classifier, test_samples):
    '''Prints precision/recall statistics of a NLTK classifier'''
    import collections
    refsets = collections.defaultdict(set)
    testsets = collections.defaultdict(set)

    for i, (sample, label) in enumerate(test_samples):
        refsets[label].add(i)
        observed = classifier.classify(sample)
        testsets[observed].add(i)

    print 'pos precision:', nltk.metrics.precision(refsets['pos'], testsets['pos'])
    print 'pos recall:', nltk.metrics.recall(refsets['pos'], testsets['pos'])
    print 'pos F-measure:', nltk.metrics.f_measure(refsets['pos'], testsets['pos'])
    print 'neg precision:', nltk.metrics.precision(refsets['neg'], testsets['neg'])
    print 'neg recall:', nltk.metrics.recall(refsets['neg'], testsets['neg'])
    print 'neg F-measure:', nltk.metrics.f_measure(refsets['neg'], testsets['neg'])


    # Organize data to get statistics on model performance
    #test_lable=[]
    #ref_lable=[]
    #for i, (sample, lable) in enumerate(testfeats):
    #    ref_lable.append(lable)
    #    observed = classifier.classify(sample)
    #    test_lable.append(observed)

if __name__ == '__main__':
    RootPath='/Users/nicolestrang/Desktop/Insight_NicoleStrang/drugs'
    
    #Read in the corpus
    df=pd.read_csv(RootPath + '/Comments.csv', index_col=0)    
    
    # Prep data for testing and training
    # First input is data from containing all the data
    # Second input is percentage of data used for training
    trainfeats,testfeats=prep_data(df,0.8)
 
    # Train the classifier and print out most infromative features and accuratcy on
    # test data 
    classifier = NaiveBayesClassifier.train(trainfeats)
    print 'accuracy:', nltk.classify.util.accuracy(classifier, testfeats)
    classifier.show_most_informative_features()
    classifier_stats(classifier, testfeats)