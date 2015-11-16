#!/bin/usr/python
"""
Created on Wed Nov 11 15:41:18 2015

@author: nicolestrang
"""
import os
import pandas as pd
import numpy as np
        
# Get list of all drug categories (folders)
def get_categories(RootPath):
    cat=[]
    for dirpath, dirnames, filenames in os.walk(RootPath):
        if filenames:
            cat.append(dirpath)
    cat.remove(RootPath)
    return cat

      
# Read in all drugs from category folder and return single df
def get_files(category):
    appended_data=[]
    for cat in category:
        cat_name=os.path.basename(cat)
        for root, dirs, files in os.walk(cat):
            for name in files:
                df=pd.read_pickle(cat + '/' + name)
                df['Drug']=name[:-2] # Remove file ext from name
                df['Category']=cat_name
                appended_data.append(df)
    appended_data=pd.concat(appended_data, axis=0)           
    return appended_data
    
# Clean data for building sentiment analysis model
def clean_data(df):    
    
    # Get rid of all entries without comments
    df['Comments'].replace('', np.nan, inplace=True)
    df.dropna(subset=['Comments'], inplace=True)

    # Get rid of duplicates
    df=df.drop_duplicates(subset=['Drug','Comments'])

    # Only retain comments with a rating of 1,2,4 or 5
    df.Rating=df.Rating.astype('float')
    df=df[df.Rating!=3]

    # Give comments a label of positive or negative based on rating 
    df['Value']=['pos' if x>3 else 'neg' for x in df['Rating']]
    
    return df            
      
if __name__ == "__main__":
    RootPath='/Users/nicolestrang/Desktop/Insight_NicoleStrang/drugs'
    
    # Get all the catergories with drug data    
    cats=get_categories(RootPath)
    
    # Read in all comments and return single datframe    
    df=get_files(cats)
    
    #Clean data 
    df=clean_data(df)

    # Save out comments as csv file
    df.to_csv(RootPath + '/Comments.csv', encoding='utf-8')
