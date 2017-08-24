import argparse
import re
import os
import csv
import math
import collections as coll


def parse_argument():
    """
    Code for parsing arguments
    """
    parser = argparse.ArgumentParser(description='Parsing a file.')
    parser.add_argument('--train', nargs=1, required=True)
    parser.add_argument('--test', nargs=1, required=True)
    args = vars(parser.parse_args())
    return args


def parse_file(filename):
    """
    Given a filename outputs user_ratings and movie_ratings dictionaries

    Input: filename

    Output: user_ratings, movie_ratings
        where:
            user_ratings[user_id] = {movie_id: rating}
            movie_ratings[movie_id] = {user_id: rating}
    """
    user_ratings = {}
    movie_ratings = {}
    # Your code here
    with open(filename) as f:
        lines = csv.reader(f)
        for line in lines:
            if int(line[1]) in user_ratings:
                user_ratings[int(line[1])][int(line[0])] = float(line[2])
            else:
                user_ratings[int(line[1])] = coll.defaultdict(list)
                user_ratings[int(line[1])][int(line[0])] = float(line[2])
            if int(line[0]) in movie_ratings:
                movie_ratings[int(line[0])][int(line[1])] = float(line[2])
            else:
                movie_ratings[int(line[0])] = coll.defaultdict(list)
                movie_ratings[int(line[0])][int(line[1])] = float(line[2])
    return user_ratings, movie_ratings


def compute_average_user_ratings(user_ratings):
    """ Given a the user_rating dict compute average user ratings

    Input: user_ratings (dictionary of user, movies, ratings)
    Output: ave_ratings (dictionary of user and ave_ratings)
    """
    ave_ratings = {}
    # Your code here
    for key in user_ratings:
        ratings = user_ratings[key].values()
        ave_ratings[key] = sum(ratings) / len(ratings)
    return ave_ratings


def compute_user_similarity(d1, d2, ave_rat1, ave_rat2):
    """ Computes similarity between two users

        Input: d1, d2, (dictionary of user ratings per user) 
            ave_rat1, ave_rat2 average rating per user (float)
        Ouput: user similarity (float)
    """
    # Your code here
    k1 = d1.keys()
    k2 = d2.keys()
    common = list(set(k1) & set(k2))
    if not common:
        return 0.0
    else:
        numerator_sum = []
        denominator_sum1 = []
        denominator_sum2 = []
        for movie in common:
            numerator_sum.append((d1[movie] - ave_rat1) * (d2[movie] - ave_rat2))
            denominator_sum1.append((d1[movie] - ave_rat1) ** 2)
            denominator_sum2.append((d2[movie] - ave_rat2) ** 2)
        if sum(denominator_sum1) == 0 or sum(denominator_sum2) == 0:
            return 0.0
        else:
            return sum(numerator_sum) / math.sqrt(sum(denominator_sum1) * sum(denominator_sum2))


def main():
    """
    This function is called from the command line via
    
    python cf.py --train [path to filename] --test [path to filename]
    """
    args = parse_argument()
    train_file = args['train'][0]
    test_file = args['test'][0]
    print train_file, test_file
    # your code here
    train_user_ratings, train_movie_ratings = parse_file(train_file)
    ave_ratings = compute_average_user_ratings(train_user_ratings)
    test_user_ratings, test_movie_ratings = parse_file(test_file)
    similarity_dict = {}
    predictions = {}
    for user in test_user_ratings:
        for movie in test_user_ratings[user]:
            other_users = train_movie_ratings[movie].keys()
            sum_numerator = []
            sum_denominator = []
            for other_user in other_users:
                if (user, other_user) in similarity_dict:
                    similarity = similarity_dict[(user, other_user)]
                elif (other_user, user) in similarity_dict:
                    similarity = similarity_dict[(other_user, user)]
                else:
                    similarity_dict[(user, other_user)] = compute_user_similarity(train_user_ratings[user], train_user_ratings[other_user], ave_ratings[user], ave_ratings[other_user])
                    similarity = similarity_dict[(user, other_user)]
                sum_numerator.append(similarity * (train_user_ratings[other_user][movie] - ave_ratings[other_user]))
                sum_denominator.append(abs(similarity))
            if sum(sum_denominator) == 0:
                prediction = ave_ratings[user]
            else:
                prediction = ave_ratings[user] + (1 / sum(sum_denominator)) * (sum(sum_numerator))
            if user in predictions:
                predictions[user][movie] = prediction
            else:
                predictions[user] = coll.defaultdict(list)
                predictions[user][movie] = prediction
    with open(test_file) as f:
        lines = csv.reader(f)
        f2 = open('predictions.txt', 'w')
        sum_rmse = []
        sum_mae = []
        for line in lines:
            user = float(line[1])
            movie = float(line[0])
            observed = float(line[2])
            sum_rmse.append((observed - predictions[user][movie]) ** 2)
            sum_mae.append(abs(observed - predictions[user][movie]))
            f2.write(','.join(line) + ','+ str(predictions[user][movie]) + '\n')
    f2.close()
    rmse = math.sqrt(sum(sum_rmse) / len(sum_rmse))
    mae = sum(sum_mae) / len(sum_mae)
    print "RMSE " + str(rmse)
    print "MAE " + str(mae)

if __name__ == '__main__':
    main()

