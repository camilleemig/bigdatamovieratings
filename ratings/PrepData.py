from csv import reader
import pandas as pd
from scipy.sparse import csr_matrix
import gc

class PrepData:
    def __init__(self):
        self.path_movies = 'ratings/ml-latest-small/movies.csv'
        self.path_ratings = 'ratings/ml-latest-small/ratings.csv'
        self.movie_rating_thres = 50
        self.user_rating_thres = 50

        self.indices_to_movies = {}
        self.movies_to_genres = {}
        self.movie_ratings = {}
        self.all_movies = set()
        self.genres = {}
        self.users_to_ratings = {}
        self.users_to_genre_ratings = {}
        self.movie_user_mat_sparse = None
        self.movies_to_indices = None

    def read_movies(self):
        movies_file = reader(open(self.path_movies))
        next(movies_file, None)
        for line in movies_file:
            movie_id = int(line[0])
            self.indices_to_movies[movie_id] = line[1]

            # get the genres for the movie
            current_genres = line[2].split('|')
            for genre in current_genres:
                if genre not in self.genres:
                    self.genres[genre] = set()
                self.genres[genre].add(line[1])
            self.movies_to_genres[line[1]] = current_genres

        self.all_movies = set(self.indices_to_movies.values())

    def read_ratings(self):
        # HAVE to have movies first!
        assert self.indices_to_movies != {}

        ratings_file = reader(open(self.path_ratings))
        next(ratings_file, None)
        temp_users_to_genre_ratings = {}
        movie_ratings = {}
        for line in ratings_file:
            # get basic data from the line
            user_id = int(line[0])
            movie_id = int(line[1])
            movie_name = self.indices_to_movies[movie_id]
            rating = float(line[2])
            # store the rating of this movie IN BOTH DIRECTIONS!
            if user_id not in self.users_to_ratings:
                self.users_to_ratings[user_id] = {}
            self.users_to_ratings[user_id][movie_name] = rating

            if movie_id not in movie_ratings:
                movie_ratings[movie_id] = []
            movie_ratings[movie_id].append(rating)

            # store the rating of the movie for the user's genre ratings
            if user_id not in temp_users_to_genre_ratings:
                temp_users_to_genre_ratings[user_id] = {}
            for genre in self.movies_to_genres[movie_name]:
                if genre not in temp_users_to_genre_ratings[user_id]:
                    temp_users_to_genre_ratings[user_id][genre] = []
                temp_users_to_genre_ratings[user_id][genre].append(rating)

        # convert user genre ratings to one average instead a list of ratings
        for user, genres in temp_users_to_genre_ratings.items():
            self.users_to_genre_ratings[user] = {}
            for genre, ratings in genres.items():
                self.users_to_genre_ratings[user][genre] = sum(ratings) / len(ratings)
        self.movie_ratings = dict((k, sum(l)/len(l)) for k, l in movie_ratings.items())

    def prep_movies_data(self):
        """
        prepare data for recommender
        1. movie-user scipy sparse matrix
        2. hashmap of movie to row index in movie-user scipy sparse matrix
        """
        # read data
        df_movies = pd.read_csv(
            self.path_movies,
            usecols=['movieId', 'title'],
            dtype={'movieId': 'int32', 'title': 'str'})
        df_ratings = pd.read_csv(
            self.path_ratings,
            usecols=['userId', 'movieId', 'rating'],
            dtype={'userId': 'int32', 'movieId': 'int32', 'rating': 'float32'})
        # filter data
        df_movies_cnt = pd.DataFrame(
            df_ratings.groupby('movieId').size(),
            columns=['count'])

        popular_movies = list(set(df_movies_cnt.query('count >= @self.movie_rating_thres').index))
        movies_filter = df_ratings.movieId.isin(popular_movies).values

        df_users_cnt = pd.DataFrame(
            df_ratings.groupby('userId').size(),
            columns=['count'])
        active_users = list(set(df_users_cnt.query('count >= @self.user_rating_thres').index))  # noqa
        users_filter = df_ratings.userId.isin(active_users).values

        df_ratings_filtered = df_ratings[movies_filter & users_filter]

        # pivot and create movie-user matrix
        movie_user_mat = df_ratings_filtered.pivot(
            index='movieId', columns='userId', values='rating').fillna(0)
        # create mapper from movie title to index
        movies_to_indices = {
            movie: i for i, movie in
            enumerate(list(df_movies.set_index('movieId').loc[movie_user_mat.index].title))  # noqa
        }
        # transform matrix to scipy sparse matrix
        movie_user_mat_sparse = csr_matrix(movie_user_mat.values)

        # clean up
        del df_movies, df_movies_cnt, df_users_cnt
        del df_ratings, df_ratings_filtered, movie_user_mat
        gc.collect()
        self.movie_user_mat_sparse = movie_user_mat_sparse
        self.movies_to_indices = movies_to_indices

    def prep_data(self):
        self.read_movies()
        self.read_ratings()     # read ratings depends on read movies
