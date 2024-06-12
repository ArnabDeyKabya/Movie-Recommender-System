

import numpy as np
import pandas as pd
import nltk
from sklearn.metrics.pairwise import cosine_similarity
from nltk.stem.porter import PorterStemmer
import ast
import pickle
from sklearn.feature_extraction.text import CountVectorizer

ps = PorterStemmer()

def stem(text):
    try:
        y = []
        for i in text.split():
            y.append(ps.stem(i))
        return " ".join(y)
    except Exception as e:
        print(f"Error in stemming: {e}")
        return text

def convert(text):
    try:
        L = []
        for i in ast.literal_eval(text):
            L.append(i['name'])
        return L
    except Exception as e:
        print(f"Error in converting: {e}")
        return []

def convert3(text):
    try:
        L = []
        counter = 0
        for i in ast.literal_eval(text):
            if counter < 3:
                L.append(i['name'])
            counter += 1
        return L
    except Exception as e:
        print(f"Error in converting top 3: {e}")
        return []

def fetch_director(text):
    try:
        L = []
        for i in ast.literal_eval(text):
            if i['job'] == 'Director':
                L.append(i['name'])
        return L
    except Exception as e:
        print(f"Error in fetching director: {e}")
        return []

def collapse(L):
    try:
        L1 = []
        for i in L:
            L1.append(i.replace(" ",""))
        return L1
    except Exception as e:
        print(f"Error in collapsing: {e}")
        return L

# Load datasets
try:
    movies = pd.read_csv('tmdb_5000_movies.csv')
    credits = pd.read_csv('tmdb_5000_credits.csv')
except Exception as e:
    print(f"Error loading datasets: {e}")

# Merge datasets
try:
    movies = movies.merge(credits, on='title')
except Exception as e:
    print(f"Error merging datasets: {e}")

# Select relevant columns
movies = movies[['movie_id', 'title', 'overview', 'genres', 'keywords', 'cast', 'crew']]

# Drop missing values
movies.dropna(inplace=True)

# Apply conversion functions
movies['genres'] = movies['genres'].apply(convert)
movies['keywords'] = movies['keywords'].apply(convert)
movies['cast'] = movies['cast'].apply(convert3)
movies['cast'] = movies['cast'].apply(lambda x: x[:3])
movies['crew'] = movies['crew'].apply(fetch_director)

# Collapse lists into strings
movies['cast'] = movies['cast'].apply(collapse)
movies['crew'] = movies['crew'].apply(collapse)
movies['genres'] = movies['genres'].apply(collapse)
movies['keywords'] = movies['keywords'].apply(collapse)

# Prepare tags
movies['overview'] = movies['overview'].apply(lambda x: x.split())
movies['tags'] = movies['overview'] + movies['genres'] + movies['keywords'] + movies['cast'] + movies['crew']

# Create new dataframe with tags
new = movies.drop(columns=['overview', 'genres', 'keywords', 'cast', 'crew'])
new['tags'] = new['tags'].apply(lambda x: " ".join(x))
new['tags'] = new['tags'].apply(stem)

# Vectorize tags and compute similarity matrix
try:
    cv = CountVectorizer(max_features=5000, stop_words='english')
    vectors = cv.fit_transform(new['tags']).toarray()
    similarity = cosine_similarity(vectors)
except Exception as e:
    print(f"Error in vectorizing and computing similarity: {e}")

# Recommendation function
def recommend(movie):
    try:
        index = new[new['title'] == movie].index[0]
        distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
        r = []
        for i in distances[1:6]:
            r.append(new.iloc[i[0]].title)
        print(r)
    except Exception as e:
        print(f"Error in recommending movies: {e}")

# Example recommendation
recommend('Avatar')

# Save the processed data and similarity matrix
try:
    pickle.dump(new, open('movie_list.pkl', 'wb'))
    pickle.dump(similarity, open('similarity.pkl', 'wb'))
except Exception as e:
    print(f"Error saving pickle files: {e}")
