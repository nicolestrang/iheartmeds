# iheartmeds

This is the repo for my project for the summer 2015 Insight Health Data Science session in Boston, MA.
For this project I was a consultant to a Fortune 500 healthcare company. The company's goal was to be able
to take advantage of customer's reviews on social media to optimize pricing and distribution strategies.
To accomplish this goal I webscraped over 13000 comments about drugs from AskAPatient and built a Naive
Bayes classifier for sentiment analysis of the comments. With this, the company is able to determine the
relative popularity of drugs that they distribute

This repo houses the three script used to colled the data, and train and test the model:

1. ScrapeAsk.py
	-input: url to category page of AskAPatient (specified in script)
	-output: directory named drugs which contains a folder for each category of drugs, which contains
		 a pickle file for each drug retrieved from scraping. 

	Webscrape AskAPatient data from the google cache, and save data locally

2. clean_data.py
	-input: RootPath to drugs directory (specified in script)
	-output: Comments.csv (saved to drugs folder)

	Concatenate all data into single dataframe, remove duplicates, and lable comments as positive or
	negative.

3. Sentiment.py
	-input: Comments.csv
	-output: Classifier performace printed to screen

	Data transformed for sentiment analysis classification with NLTK, stopwords removed.
	Naive Bayes model trained on 80% of the data and tested on the remaining 20%.
