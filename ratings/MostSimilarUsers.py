from operator import itemgetter
from math import sqrt
from . PrepData import PrepData
import time

def find_cosine_similarity(ratings1, ratings2):
    d1 = 0
    d2 = 0
    dot = 0
    for movie in ratings1:
        rating1 = ratings1[movie]
        rating2 = ratings2[movie]
        dot += rating1*rating2
        d1 += rating1*rating1
        d2 += rating2*rating2
    return dot / (sqrt(d1)*sqrt(d2))


def find_predicted_ratings_for_user(user_id):
    data = PrepData()
    data.prep_data()

    sorted_users = sorted(data.users_to_ratings.keys())
    test_users_movies = set(data.users_to_ratings[user_id].keys())
    test_users_movies_with_ratings = data.users_to_ratings[user_id]
    # shared movies is stored as user_id -> set of shared movies
    shared_movies = {}
    for user in sorted_users[1:]:
        shared_movies[user] = test_users_movies & set(data.users_to_ratings[user].keys())

    # similarities is stored as user_id -> user_similarity
    similarities = {}
    for user in sorted_users[1:]:
        if not shared_movies[user]:
            continue
        user1_movies = dict([(k, v) for k,v in test_users_movies_with_ratings.items() if k in shared_movies[user]])
        user2_movies = dict([(k, v) for k,v in data.users_to_ratings[user].items() if k in shared_movies[user]])
        similarity = find_cosine_similarity(user1_movies, user2_movies)
        similarities[user] = similarity

    # user averages is user_id -> average of all their ratings
    user_averages = {}
    for user in sorted_users:
        ratings = list(data.users_to_ratings[user].values())
        average = sum(ratings)/len(ratings)
        user_averages[user] = average

    # predicted ratings is movie name -> predicted rating
    predicted_ratings = {}
    test_user_average = user_averages[user_id]
    for movie in data.all_movies - test_users_movies:
        total_sim = 0
        total_sim_rated = 0
        for user in sorted_users[1:]:
            if movie not in data.users_to_ratings[user] or user not in similarities:
                continue
            similarity = similarities[user]
            total_sim += similarity
            total_sim_rated += similarity*(data.users_to_ratings[user][movie] - user_averages[user])
        if total_sim == 0 or total_sim_rated == 0:
            predicted_ratings[movie] = test_user_average
            continue
        predicted = total_sim_rated/total_sim
        predicted_ratings[movie] = test_user_average + predicted
    return sorted(predicted_ratings.items(), key=itemgetter(1), reverse=True)

#
# t0 = time.time()
#
# print(find_predicted_ratings_for_user(1))
# print('It took my system {:.2f}s to get top n movies \n\
#               '.format(time.time() - t0))