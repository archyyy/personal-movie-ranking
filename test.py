import requests
from pprint import pprint

API_KEY = "089dc0726eb00c1537cb3c254c992ca6"

def get_movie(movie_id):
    response = requests.get(
        url=f"https://api.themoviedb.org/3/movie/{movie_id}", params={"api_key": API_KEY}
    )
    data = response.json()
    pprint(data)


movies = get_movie(684426)
