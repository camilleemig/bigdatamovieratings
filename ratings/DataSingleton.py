from . PrepData import PrepData

class DataSingleton:
    class __DataSingleton:
        def __init__(self):
            prepper = PrepData()
            prepper.read_movies()
            prepper.read_ratings()
            prepper.prep_movies_data()
            self.indices_to_movies = prepper.indices_to_movies
            self.movies_to_indices = prepper.movies_to_indices
            self.movies_to_genres = prepper.movies_to_genres
            self.all_movies = prepper.all_movies
            self.genres = prepper.genres
            self.users_to_ratings = prepper.users_to_ratings
            self.users_to_genre_ratings = prepper.users_to_genre_ratings
            self.movie_user_mat_sparse = prepper.movie_user_mat_sparse

    instance = None
    def __init__(self):
        if not DataSingleton.instance:
            DataSingleton.instance = DataSingleton.__DataSingleton()

    def __getattr__(self, name):
        return getattr(self.instance, name)
