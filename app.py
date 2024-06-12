
import streamlit as st
import pickle
import pandas as pd
import requests
from streamlit.components.v1 import components

new = pickle.load(open('movie_list.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
        data = requests.get(url).json()
        poster_path = data.get('poster_path')
        if poster_path:
            full_path = f"https://image.tmdb.org/t/p/w500/{poster_path}"
            return full_path
        else:
            return "No poster available"
    except Exception as e:
        print(f"Error fetching poster: {e}")
        return "Error fetching poster"

def fetch_trailer(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
        data = requests.get(url).json()
        trailers = [video for video in data['results'] if video['type'] == 'Trailer' and video['site'] == 'YouTube']
        if trailers:
            trailer_url = f"https://www.youtube.com/watch?v={trailers[0]['key']}"
            return trailer_url
        else:
            return None
    except Exception as e:
        print(f"Error fetching trailer: {e}")
        return None

def recommend(movie):
    try:
        index = new[new['title'] == movie].index[0]
        distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
        recommended_movies = []
        posters = []
        trailers = []
        for i in distances[1:6]:
            movie_id = new.iloc[i[0]].movie_id
            recommended_movies.append(new.iloc[i[0]].title)
            posters.append(fetch_poster(movie_id))
            trailers.append(fetch_trailer(movie_id))
        return recommended_movies, posters, trailers
    except Exception as e:
        print(f"Error during recommendation: {e}")
        return [], [], []

movies = pd.DataFrame(new)

st.title('Movie Recommender System')

option = st.selectbox('Search Your movie', movies['title'].values)

if st.button('Recommend'):
    r, posters, trailers = recommend(option)
    col1, col2, col3, col4, col5 = st.columns(5)

    cols = [col1, col2, col3, col4, col5]

    for i in range(5):
        with cols[i]:
            if i < len(r):
                st.text(r[i])
                st.image(posters[i])
                if trailers[i]:
                    trailer_url = trailers[i]
                    button_html = f'''
                                <a href="{trailer_url}" target="_blank">
                                    <button style="background-color:Transparent;
                                                   border: none;
                                                   color: blue;
                                                   text-decoration: underline;
                                                   cursor: pointer;">Watch Trailer</button>
                                </a>
                                '''
                    st.markdown(button_html, unsafe_allow_html=True)
            else:
                st.text("No recommendation")

