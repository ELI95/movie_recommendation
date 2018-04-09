import sys
import random
import math
import os
from operator import itemgetter


random.seed(0)


class UserBasedCF(object):
    def __init__(self):
        self.train_set = {}
        self.test_set = {}

        self.n_sim_user = 20
        self.n_rec_movie = 10

        self.user_sim_mat = {}
        self.movie_popular = {}
        self.movie_count = 0

    @staticmethod
    def loadfile(filename):
        """
         load a file, return a generator. 
        """
        fp = open(filename, 'r')
        for i, line in enumerate(fp):
            yield line.strip('\r\n')
        fp.close()
        print('load %s succeed' % filename, file=sys.stderr)

    def generate_dataset(self, filename, pivot=0.7):
        train_set_len = 0
        test_set_len = 0
        for line in self.loadfile(filename):
            user, movie, rating, _ = line.split('::')
            if random.random() < pivot:
                self.train_set.setdefault(user, {})
                self.train_set[user][movie] = int(rating)
                train_set_len += 1
            else:
                self.test_set.setdefault(user, {})
                self.test_set[user][movie] = int(rating)
                test_set_len += 1

        print('split training set and test set succeed', file=sys.stderr)
        print('train set = %s' % train_set_len, file=sys.stderr)
        print('test set = %s' % test_set_len, file=sys.stderr)

    def calc_user_sim(self):
        """
        calculate user similarity matrix
        """
        movie2users = dict()
        for user, movies in self.train_set.items():
            for movie in movies:
                if movie not in movie2users:
                    movie2users[movie] = set()
                movie2users[movie].add(user)
                if movie not in self.movie_popular:
                    self.movie_popular[movie] = 0
                self.movie_popular[movie] += 1
        print('build movie-users inverse table succeed', file=sys.stderr)

        self.movie_count = len(movie2users)
        print('total movie number = %d' % self.movie_count, file=sys.stderr)

        usersim_mat = self.user_sim_mat
        for movie, users in movie2users.items():
            for u in users:
                for v in users:
                    if u == v:
                        continue
                    usersim_mat.setdefault(u, {})
                    usersim_mat[u].setdefault(v, 0)
                    usersim_mat[u][v] += 1
        print('build user co-rated movies matrix succeed', file=sys.stderr)

        sim_factor_count = 0
        print_step = 2000000
        for u, related_users in usersim_mat.items():
            for v, count in related_users.items():
                usersim_mat[u][v] = count / math.sqrt(
                    len(self.train_set[u]) * len(self.train_set[v]))
                sim_factor_count += 1
                if sim_factor_count % print_step == 0:
                    print('calculating user similarity factor(%d)' % sim_factor_count, file=sys.stderr)

        print('calculate user similarity matrix(similarity factor) succeed', file=sys.stderr)
        print('Total similarity factor number = %d' % sim_factor_count, file=sys.stderr)

    def recommend(self, user):
        """
        Find K similar users and recommend N movies.
        """
        K = self.n_sim_user
        N = self.n_rec_movie
        rank = dict()
        watched_movies = self.train_set[user]

        for similar_user, similarity_factor in sorted(self.user_sim_mat[user].items(),
                                                      key=itemgetter(1), reverse=True)[0:K]:
            for movie in self.train_set[similar_user]:
                if movie in watched_movies:
                    continue
                rank.setdefault(movie, 0)
                rank[movie] += similarity_factor
        return sorted(rank.items(), key=itemgetter(1), reverse=True)[0:N]

    def evaluate(self):
        """
        print evaluation result: precision, recall, coverage and popularity
        """
        N = self.n_rec_movie
        #  varables for precision and recall
        hit = 0
        rec_count = 0
        test_count = 0
        # varables for coverage
        all_rec_movies = set()
        # varables for popularity
        popular_sum = 0

        for i, user in enumerate(self.train_set):
            if i % 500 == 0:
                print ('recommended for %d users' % i, file=sys.stderr)
            test_movies = self.test_set.get(user, {})
            rec_movies = self.recommend(user)
            for movie, _ in rec_movies:
                if movie in test_movies:
                    hit += 1
                all_rec_movies.add(movie)
                popular_sum += math.log(1 + self.movie_popular[movie])
            rec_count += N
            test_count += len(test_movies)

        precision = hit / (1.0 * rec_count)
        recall = hit / (1.0 * test_count)
        coverage = len(all_rec_movies) / (1.0 * self.movie_count)
        popularity = popular_sum / (1.0 * rec_count)

        print('precision=%.4f\trecall=%.4f\tcoverage=%.4f\tpopularity=%.4f' %
               (precision, recall, coverage, popularity), file=sys.stderr)


if __name__ == '__main__':
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    rating_file = os.path.join(BASE_DIR, 'datasets/ml-1m/ratings.dat')
    user_cf = UserBasedCF()
    user_cf.generate_dataset(rating_file)
    user_cf.calc_user_sim()
    user_cf.evaluate()
