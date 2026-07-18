import requests
from pathlib import Path

import streamlit as st
import pickle


st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="centered")
st.title("Movie Recommendation System")
st.markdown(
    """
    <style>
        .movie-card {
            padding: 0.75rem;
            border-radius: 14px;
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.08);
            text-align: center;
            margin-bottom: 0.75rem;
        }
        .movie-card img {
            border-radius: 12px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

BASE_DIR = Path(__file__).resolve().parent

with open(BASE_DIR / 'movies_dict.pkl', 'rb') as f:
     movies = pickle.load(f)

movie_titles = movies["title"].values
with open(BASE_DIR / 'similarity.pkl', 'rb') as f:
    similarity = pickle.load(f)

control_left, control_right = st.columns([3, 1])
with control_left:
    option = st.selectbox('Select a movie:', movie_titles)
with control_right:
    top_n = st.slider('Top picks', min_value=3, max_value=10, value=6)


def fetch_poster(movie_id):
    try:
        response = requests.get(
            'https://api.themoviedb.org/3/movie/{movie_id}?api_key={YOUR API KEY}&language=en-US'.format(movie_id=movie_id),
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            return "https://image.tmdb.org/t/p/w500/" + poster_path
    except requests.RequestException:
        pass

    return "https://via.placeholder.com/500x750?text=No+Poster"
   

def recommend(movie):
  recommended_movies_posters=[]
  movie_index=movies[movies["title"]==movie].index[0]
  distance=similarity[movie_index]
  movies_list=sorted(list(enumerate(distance)),reverse=True,key=lambda x:x[1])[0:10]
  recommended_movies=[]
  for i in movies_list:
      movie_row = movies.iloc[i[0]]
      recommended_movies_posters.append(fetch_poster(movie_row.movie_id))
      recommended_movies.append(movie_row.title)
  return recommended_movies, recommended_movies_posters

if st.button('Recommend', use_container_width=True):
   recommended_movies, recommendeed_movies_posters = recommend(option)
   recommended_movies = recommended_movies[:top_n]
   recommendeed_movies_posters = recommendeed_movies_posters[:top_n]

   st.write('You selected:', option)
   st.write('Recommended movies:')

   for start in range(0, len(recommended_movies), 3):
       row_movies = recommended_movies[start:start + 3]
       row_posters = recommendeed_movies_posters[start:start + 3]
       cols = st.columns(3)
       for col, movie, poster in zip(cols, row_movies, row_posters):
           with col:
               st.markdown('<div class="movie-card">', unsafe_allow_html=True)
               st.image(poster, use_container_width=True)
               st.markdown(f"**{movie}**")
               st.markdown('</div>', unsafe_allow_html=True)
