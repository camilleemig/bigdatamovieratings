from csv import reader


class PrepData:
    def __init__(self):
        self.indices_to_movies = {}
        self.movies_to_genres = {}
        self.all_movies = set()
        self.genres = {}
        self.users_to_ratings = {}
        self.users_to_genre_ratings = {}

    def read_movies(self):
        movies_file = reader(open('ratings/ml-latest-small/movies.csv'))
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

        ratings_file = reader(open('ratings/ml-latest-small/ratings.csv'))
        next(ratings_file, None)
        temp_users_to_genre_ratings = {}
        for line in ratings_file:
            # get basic data from the line
            user_id = int(line[0])
            movie_id = int(line[1])
            movie_name = self.indices_to_movies[movie_id]
            rating = float(line[2])
            # store the rating of this movie
            if user_id not in self.users_to_ratings:
                self.users_to_ratings[user_id] = {}
            self.users_to_ratings[user_id][movie_name] = rating

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

    def prep_data(self):
        self.read_movies()
        self.read_ratings()     # read ratings depends on read movies
