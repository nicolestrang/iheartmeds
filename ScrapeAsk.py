#!/bin/usr/python
"""
Script to scrape data from Google cache of AskAPatient website
@author: nicolestrang
"""
import requests
import requests.exceptions
import time
import random
from bs4 import BeautifulSoup
import unicodedata
import numpy as np
import pandas as pd
import os
MAX_WAIT=20

# FUNCTIONS
# Function to load user agents
def LoadUserAgents(uafile='USER_AGENTS_FILE'):
    """
    uafile : string
        path to text file of user agents, one per line
    """
    uas = []
    with open(uafile, 'rb') as uaf:
        for ua in uaf.readlines():
            if ua:
                uas.append(ua.strip()[1:-1-1])
    random.shuffle(uas)
    return uas

# Function to return data from url
def Return_url(proxies, url, user_agents):
    #user_agents = LoadUserAgents(uafile)
    ua = random.choice(user_agents)  # select a random user agent
    headers = {
        "Connection" : "close",  
        "User-Agent" : ua}
    random.shuffle(proxies)
    for p in proxies:
        proxy = {"http": "http://" + p}
        time.sleep(MAX_WAIT*random.random())      
        r = requests.get(url, proxies=proxy, headers=headers)
        if (r.status_code==200):
            msg="Found a good proxy!"            
            break
        elif (r.status_code==404):
            msg=('Link for ' + url + ' broken!!')            
            break
    return(r, msg)
        
# Function to strip table out of html page
def get_table(r,data):        
    soup = BeautifulSoup(r.text, "lxml")
    table=soup.find('table', {'class': 'ratingsTable'})
    cells=table.findAll('td')
    for cell in cells:
        if 'td bgcolor' in str(cell):
            data.append(unicodedata.normalize('NFKD',cell.text))
    return data

# Return only upper case characters
def only_upper(s):
        return filter(lambda x: x.isupper(), s)      
    
   
if __name__ == '__main__':

    # Outpath
    outpath='/Users/nicolestrang/Desktop/Insight_NicoleStrang/drugs/'

    cache_url=('http://webcache.googleusercontent.com/search?q=cache:' + 
            'http://www.askapatient.com')

    # Proxy List
    proxies = [] # Need to get proxies for this script
    
    # Import user agents to a list
    user_agents = LoadUserAgents('user_agents.txt')

    # Get a list of URL to list of drugs in a category
    DrugCatList=[]
    cat_url=(cache_url + '/comparedrugslist.asp')
    (r,msg)=Return_url(proxies, cat_url)    
    print msg
    soup = BeautifulSoup(r.text, "lxml")
    soup.prettify()
    for anchor in soup.findAll('a', href=True):
        if 'comparedrugs' in anchor['href'] and 'class=' in anchor['href']:
            DrugCatList.append(anchor['href'])
            
    # Fix dashes
    DrugCatList = [d.replace('%2', '-') for d in DrugCatList]            
                       
    # For each category get a list of the links to the drugs        
    for drug_cat in DrugCatList:
    
        # Check whether drug category URl begins with a slash
        if not drug_cat[0]=='/':
            drug_cat=('/' + drug_cat)
    
        # Get the drug category name from the URL        
        drug_cat_name=only_upper(drug_cat) 
    
        # Create folder for drug category if it doesn't exist
        if not os.path.exists(outpath + drug_cat_name):
            os.makedirs(outpath + drug_cat_name)
        DrugList=[]    
        url=(cache_url + drug_cat)
        (r,msg)=Return_url(proxies, url)
        print msg
        print( 'Got ' + drug_cat_name + ' category !!')
        if r.status_code==404:
            print (url + '' + drug_cat_name)
            continue
        soup = BeautifulSoup(r.text, "lxml")
        soup.prettify()
        for anchor in soup.findAll('a', href=True):
            if 'viewrating' in anchor['href']:
                DrugList.append(anchor['href']) 
            
        # Fix dashes          
        DrugList = [d.replace('%2', '-') for d in DrugList]  

        # loop through all the drugs in the category    
        for drug in DrugList:   
            #Get the name of the drug
            name=only_upper(drug)
        
        #Check whetner a file exists with that name
        if os.path.isfile(outpath + 'drugs/' + drug_cat_name + '/'+ name + '.csv'):
            continue
        
        drug_url = (cache_url + drug)        
        
        print ('Getting data for ' + name) 
    
        (r,msg)=Return_url(proxies, drug_url)    
        print msg
    
        #If link doesn't exist move on to next drug in list
        if r.status_code==404:
            continue
        
        #Pull the data of interest out of page 1
        data=[]          
        data=get_table(r,data)
            
        #Reshape data and create dataframe
        data=np.array(data)
        data=np.reshape(data,(-1,8))
        df=pd.DataFrame(data=data,
                    columns=['Rating','Reason','Side Effects','Comments',
                    'Sex','Age','Duration/Dosage', 'Date Added'])
              
        #Save comments for individual drug as csv
        df.to_pickle(outpath + '/' + drug_cat_name +'/'+ name + '.p')               
