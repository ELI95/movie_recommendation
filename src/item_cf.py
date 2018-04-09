import sys
import random
import math
import os
from operator import itemgetter


random.seed(0)


class ItemBasedCF(object):
    """
    TopN recommendation - Item Based Collaborative Filtering
    """

    def __init__(self):
        self.train_set = {}
        self.test_set = {}

        self.n_sim_movie = 20
        self.n_rec_movie = 10

        self.movie_sim_mat = {}
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

    def calc_movie_sim(self):
        """
        calculate movie similarity matrix
        """
        for user, movies in self.train_set.items():
            for movie in movies:
                if movie not in self.movie_popular:
                    self.movie_popular[movie] = 0
                self.movie_popular[movie] += 1

        print('count movies number and popularity succeed', file=sys.stderr)

        # save the total number of movies
        self.movie_count = len(self.movie_popular)
        print('total movie number = %d' % self.movie_count, file=sys.stderr)

        # count co-rated users between items
        itemsim_mat = self.movie_sim_mat
        print('building co-rated users matrix...', file=sys.stderr)

        for user, movies in self.train_set.items():
            for m1 in movies:
                for m2 in movies:
                    if m1 == m2:
                        continue
                    itemsim_mat.setdefault(m1, {})
                    itemsim_mat[m1].setdefault(m2, 0)
                    itemsim_mat[m1][m2] += 1

        print('build co-rated users matrix succeed', file=sys.stderr)

        # calculate similarity matrix
        print('calculating movie similarity matrix...', file=sys.stderr)
        simfactor_count = 0
        PRINT_STEP = 2000000

        for m1, related_movies in itemsim_mat.items():
            for m2, count in related_movies.items():
                itemsim_mat[m1][m2] = count / math.sqrt(
                    self.movie_popular[m1] * self.movie_popular[m2])
                simfactor_count += 1
                if simfactor_count % PRINT_STEP == 0:
                    print('calculating movie similarity factor(%d)' %
                          simfactor_count, file=sys.stderr)

        print('calculate movie similarity matrix(similarity factor) succeed', file=sys.stderr)
        print('Total similarity factor number = %d' % simfactor_count, file=sys.stderr)

    def recommend(self, user):
        """
        Find K similar movies and recommend N movies.
        """
        K = self.n_sim_movie
        N = self.n_rec_movie
        rank = {}
        watched_movies = self.train_set[user]

        for movie, rating in watched_movies.items():
            for related_movie, similarity_factor in sorted(self.movie_sim_mat[movie].items(),
                                                           key=itemgetter(1), reverse=True)[:K]:
                if related_movie in watched_movies:
                    continue
                rank.setdefault(related_movie, 0)
                rank[related_movie] += similarity_factor * rating
        return sorted(rank.items(), key=itemgetter(1), reverse=True)[:N]

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
                print('recommended for %d users' % i, file=sys.stderr)
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
    item_cf = ItemBasedCF()
    item_cf.generate_dataset(rating_file)
    item_cf.calc_movie_sim()
    item_cf.evaluate()
