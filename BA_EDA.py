#Import needed packages
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

import pickle
import nltk
import random
import math
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk.stem import WordNetLemmatizer
nltk.download('stopwords')
nltk.download('punkt')

from sklearn.metrics.pairwise import cosine_similarity

import warnings
pd.set_option('display.max_rows', 500)
pd.set_option('display.min_rows', 100)
warnings.filterwarnings('ignore')

#Read in dataset
top_250 = pd.read_csv('top_250.csv')
top_250 = top_250.set_index('Name')
top_250.head()

#Look at styles
top_250['Style'].value_counts().index

#View donut chart
fig, axe = plt.subplots(figsize=(30, 30))
colors = sns.color_palette('pastel')
plt.pie(top_250['Style'].value_counts().values, 
        labels = top_250['Style'].value_counts().index, 
        colors = colors, 
        autopct='%.0f%%',
        textprops={'fontsize': 20})
my_circle=plt.Circle( (0,0), 0.7, color='white')
p=plt.gcf()
p.gca().add_artist(my_circle)
plt.show()

#Create vectorized dataframe
cv = CountVectorizer(lowercase = False, min_df = 4)

style = cv.fit_transform(top_250['Style'])
style_df = pd.DataFrame(style.todense(), columns = cv.get_feature_names())

style_df.set_index(top_250.index, inplace = True)

style_df

#Highest rated by style
avg_rating_by_style = pd.DataFrame(top_250.groupby(['Style']).agg({'Avg Rating':['mean', 'count']})).reset_index()
avg_rating_by_style.columns = ['Style', 'Avg Rating','Count']
avg_rating_by_style.head()

#Most rated of the top beers 
avg_rating_by_style.sort_values(by = 'Count', ascending = False).head(15)

#Avg Ratings Histogram
fig, axe = plt.subplots(figsize=(10, 10))
plt.title('Avg Ratings Histogram')
sns.histplot(data = top_250, x = 'Avg Rating')

#ABV Histogram
fig, axe = plt.subplots(figsize=(10, 10))
plt.title('ABV Histogram')
sns.histplot(data = top_250, x = 'ABV')

#What is that beer with a crazy high abv?
top_250[top_250['ABV']==top_250.ABV.max()]

#Score Histogram
fig, axe = plt.subplots(figsize=(10, 10))
plt.title('Score Histogram')
sns.histplot(data = top_250, x = 'Score')

#Create lemmatizer
stop_words = stopwords.words('english')
lemmatizer = WordNetLemmatizer()

def lemmatize(text):
    
    tokens = nltk.word_tokenize(text)
    tokens = [token.lower() for token in tokens]
    tokens = [token for token in tokens if token not in stop_words]
    tokens = [token for token in tokens if token.isalpha()]
    tokens = [lemmatizer.lemmatize(token) for token in tokens]
    tokens = [token for token in tokens if len(token) > 1]
    
    return tokens
  
 
#TFIDF on beer notes
tfidf = TfidfVectorizer(min_df = 5, max_df = 0.8, tokenizer = lemmatize, ngram_range = (1, 2),
                        binary = False, use_idf = True, norm = None) 

notes_tfidf = tfidf.fit_transform(top_250["Notes"])
notes_tfidf = pd.DataFrame(notes_tfidf.todense(), columns = tfidf.get_feature_names())

notes_tfidf.index = top_250.index
notes_tfidf['Avg Rating'] = top_250['Avg Rating']

notes_tfidf.head()

#What are the best/worst words for notes (among the top beers)
notes_columns = list(notes_tfidf.columns).copy()
notes_columns.remove('Avg Rating')

notes_correlations = pd.DataFrame(notes_tfidf[notes_columns].corrwith(notes_tfidf['Avg Rating'])).reset_index()
notes_correlations.columns = ['Note Token','Correlation']

notes_correlations = notes_correlations.sort_values('Correlation', ascending = False)
notes_correlations.head(20)

notes_correlations.tail(20)

#Build TFIDF for beer reviews
tfidf = TfidfVectorizer(min_df = 5, max_df = 0.8, tokenizer = lemmatize, ngram_range = (1, 2),
                        binary = False, use_idf = True, norm = None) 

reviews_tfidf = tfidf.fit_transform(top_250["reviews"])
reviews_tfidf = pd.DataFrame(reviews_tfidf.todense(), columns = tfidf.get_feature_names())

reviews_tfidf.index = top_250.index
reviews_tfidf['Avg Rating'] = top_250['Avg Rating']

reviews_tfidf.head()

#What are the best/worst tokens for reviews (among the top 250)
reviews_columns = list(reviews_tfidf.columns).copy()
reviews_columns.remove('Avg Rating')
reviews_correlations = pd.DataFrame(reviews_tfidf[reviews_columns].corrwith(reviews_tfidf['Avg Rating'])).reset_index()
reviews_correlations.columns = ['Review Token','Correlation']
reviews_correlations = reviews_correlations.sort_values('Correlation', ascending = False)

reviews_correlations.head(20)

reviews_correlations.tail(20)

#Concatenate matrices for similarity
train = pd.concat([style_df, notes_tfidf, reviews_tfidf, top_250[['ABV','Score','Avg Rating']]], axis = 1).fillna(0)
train.head()

cosine_sim = cosine_similarity(train)
indices = pd.Series(range(0, len(train.index)), index = train.index).drop_duplicates()

def get_recommendations(beer_name, cosine_sim = cosine_sim, indices = indices):
    
    # Get the index of the movie that matches the title
    idx = indices[beer_name]

    # Get the pairwsie similarity scores of all movies with that movie
    sim_scores = list(enumerate(cosine_sim[idx]))

    # Sort the movies based on the similarity scores
    sim_scores = sorted(sim_scores, key = lambda x: x[1], reverse=True)

    # Get the scores of the 10 most similar movies
    sim_scores = sim_scores[1:len(sim_scores)]

    # Get the beer indices
    beer_indices = [i[0] for i in sim_scores]
    
    recommendations_temp = pd.DataFrame({"Movies": top_250.iloc[beer_indices].index.tolist(),
                                     "Similarity": [sim[1] for sim in sim_scores]})
    
    return recommendations_temp.head(10)
  
  get_recommendations('Kentucky Brunch Brand Stout')
