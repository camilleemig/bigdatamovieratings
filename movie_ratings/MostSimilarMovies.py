# data science imports
from sklearn.neighbors import NearestNeighbors

# utils import
from fuzzywuzzy import fuzz
from operator import itemgetter
from . MovieRatingData import MovieRatingData

class KnnRecommender:
    """
    This is an item-based collaborative filtering recommender with
    KNN implmented by sklearn
    """

    def __init__(self):
        """
        Recommender requires path to data: movies data and movie_ratings data
        """

        self.model = NearestNeighbors()
        self.model.set_params(**{
            'n_neighbors': 20,
            'algorithm': 'brute',
            'metric': 'cosine',
            'n_jobs': -1})
        self.data = MovieRatingData()
        data = self.data.movie_user_mat_sparse
        self.model.fit(data)


    def _fuzzy_matching(self, movie):
        """
        return the closest match via fuzzy ratio.
        If no match found, return None
        Parameters
        ----------
        hashmap: dict, map movie title name to index of the movie in data
        fav_movie: str, name of user input movie
        Return
        ------
        index of the closest match
        """
        match_tuples = []
        # get match
        for title, idx in self.data.movies_to_csr_indices.items():
            ratio = fuzz.ratio(title.lower(), movie.lower())
            if ratio >= 60:
                match_tuples.append((title, idx, ratio))
        # sort
        return None if not match_tuples else sorted(match_tuples, key=itemgetter(2), reverse=True)[0][1]

    def _inference(self, movie):
        """
        return top n similar movie recommendations based on user's input movie
        Parameters
        ----------
        model: sklearn model, knn model
        movie: str, name of user input movie
        Return
        ------
        list of top n similar movie recommendations
        """
        data = self.data.movie_user_mat_sparse
        movie_idx = self._fuzzy_matching(movie)

        distances, indices = self.model.kneighbors(data[movie_idx],  n_neighbors=6)
        distances, indices = distances.squeeze().tolist(), indices.squeeze().tolist()
        raw_recommends = sorted(list(zip(indices, distances)), key=itemgetter(1))[:0:-1]

        # return recommendation (movieId, distance)
        return raw_recommends

    def make_recommendations(self, movie):
        """
        make top n movie recommendations
        Parameters
        ----------
        movie: str, name of user input movie
        n_recommendations: int, top n recommendations
        """
        # get recommendations
        raw_recommends = self._inference(movie)
        indices_to_movies = {v: k for k, v in self.data.movies_to_csr_indices.items()}
        movie_names = [indices_to_movies[i[0]] for i in raw_recommends]
        return movie_names