import pandas as pd
from scipy.sparse import csr_matrix

class MovieRatingData:
    class __MovieRatingData:
        def __init__(self):
            self.path_movies = 'movie_ratings/ml-latest-small/movies.csv'
            self.path_ratings = 'movie_ratings/ml-latest-small/ratings.csv'
            self.movie_rating_thres = 50
            self.user_rating_thres = 50

            self.movie_user_mat_sparse = None
            self.movies_to_csr_indices = None
            self.csr_indices_to_movies = None
            self.movieId_to_movieName = None
            self.movieName_to_movieId = None
            self.users_to_ratings = None
            self.all_movies = None
            self.movies_to_genres = None
            self.genres = None
            self.average_movie_ratings = None

            self.prep_movies_data()

        def prep_movies_data(self):
            """
            prepare data for recommender
            1. movie-user scipy sparse matrix
            2. hashmap of movie to row index in movie-user scipy sparse matrix
            """
            # read data
            df_movies = pd.read_csv(
                self.path_movies,
                usecols=['movieId', 'title', 'genres'],
                dtype={'movieId': 'int32', 'title': 'str'},
                converters={"genres": lambda x: x.strip().split("|")})
            df_ratings = pd.read_csv(
                self.path_ratings,
                usecols=['userId', 'movieId', 'rating'],
                dtype={'userId': 'int32', 'movieId': 'int32', 'rating': 'float32'})
            # filter data to get rid of any movie that has less than 50 ratings
            df_movies_cnt = pd.DataFrame(
                df_ratings.groupby('movieId').size(),
                columns=['count'])

            popular_movies = list(set(df_movies_cnt.query('count >= @self.movie_rating_thres').index))
            movies_filter = df_ratings.movieId.isin(popular_movies).values

            # filter data to get rid of any user that has rated less than 50 movies
            df_users_cnt = pd.DataFrame(
                df_ratings.groupby('userId').size(),
                columns=['count'])
            active_users = list(set(df_users_cnt.query('count >= @self.user_rating_thres').index))  # noqa
            users_filter = df_ratings.userId.isin(active_users).values

            # This gets rid of movies that were discarded from the user's ratings
            df_ratings_filtered = df_ratings[movies_filter & users_filter]

            movies_filter = df_movies.movieId.isin(popular_movies).values
            df_movies_filtered = df_movies[movies_filter]

            # pivot and create movie-user matrix
            movie_user_mat = df_ratings_filtered.pivot(
                index='movieId', columns='userId', values='rating').fillna(0)
            user_movie_mat = df_ratings_filtered.pivot(
                index='userId', columns='movieId', values='rating')
            # create mapper from movie title to index
            movies_to_csr_indices = {
                movie: i for i, movie in
                enumerate(list(df_movies.set_index('movieId').loc[movie_user_mat.index].title))  # noqa
            }
            csr_indices_to_movies = {v: k for k, v in movies_to_csr_indices.items()}
            movies_to_genres = {
                row["movieId"]: row["genres"] for index, row in df_movies_filtered.iterrows()  # noqa
            }
            movieId_to_movieName = {
                row["movieId"]: row["title"] for index, row in df_movies_filtered.iterrows()  # noqa
            }
            movieName_to_movieId = {v: k for k, v in movieId_to_movieName.items()}

            users_to_movie_ratings = {}
            movie_average_ratings = {}
            for user in user_movie_mat.index:
                users_to_movie_ratings[user] = {}
                row = user_movie_mat.loc[user]
                for movie, rating in zip(user_movie_mat.columns, row):
                    if pd.isna(rating):
                        continue
                    users_to_movie_ratings[user][movieId_to_movieName[movie]] = rating
                    if movie not in movie_average_ratings:
                        movie_average_ratings[movie] = []
                    movie_average_ratings[movie].append(rating)

            genres_to_movies = {}
            for movie, genres in movies_to_genres.items():
                for genre in genres:
                    if genre not in genres_to_movies:
                        genres_to_movies[genre] = set()
                    genres_to_movies[genre].add(movie)
            # transform matrix to scipy sparse matrix
            movie_user_mat_sparse = csr_matrix(movie_user_mat.values)

            self.movie_user_mat_sparse = movie_user_mat_sparse
            self.movies_to_csr_indices = movies_to_csr_indices
            self.csr_indices_to_movies = csr_indices_to_movies
            self.movieId_to_movieName = movieId_to_movieName
            self.movieName_to_movieId = movieName_to_movieId
            self.users_to_ratings = users_to_movie_ratings
            self.all_movies = set(self.csr_indices_to_movies.values())
            self.movies_to_genres = movies_to_genres
            self.genres = genres_to_movies
            self.average_movie_ratings = dict((k, sum(l) / len(l)) for k, l in movie_average_ratings.items())

    instance = None

    def __init__(self):
        if not MovieRatingData.instance:
            MovieRatingData.instance = MovieRatingData.__MovieRatingData()

    def __getattr__(self, name):
        return getattr(self.instance, name)
