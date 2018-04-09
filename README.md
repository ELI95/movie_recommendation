## user_cf
```python
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
```
```python
train_set 
{user: {movie: rating, ...}, ...}
```
-----

```python
movie2users = dict()
for user, movies in self.train_set.items():
    for movie in movies:
        if movie not in movie2users:
            movie2users[movie] = set()
        movie2users[movie].add(user)
```
```python
movie2users
{movie: {user, ...}, ...}
```
-----


```python
user_sim_mat = dict()
for movie, users in movie2users.items():
    for u in users:
        for v in users:
            if u == v:
                continue
            user_sim_mat.setdefault(u, {})
            user_sim_mat[u].setdefault(v, 0)
            user_sim_mat[u][v] += 1
```
```python
user_sim_mat
{user_0: {user_1: count, ...}, ...}

```
-----


```python
for u, related_users in usersim_mat.items():
    for v, count in related_users.items():
        usersim_mat[u][v] = count / math.sqrt(len(self.train_set[u]) * len(self.train_set[v]))
```
```python
user_sim_mat
{user_0: {user_1: similarity, ...}, ...}
```
-----


```python
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
```
```python
[(movie, recommendation_value), ...]
```

</br>
## item_cf
```python
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
```
```python
train_set
{user: {movie: rating, ...}, ...}
```
-----

```python
for user, movies in self.train_set.items():
    for movie in movies:
        if movie not in self.movie_popular:
            self.movie_popular[movie] = 0
        self.movie_popular[movie] += 1
```
```python
movie_popular
{movie: count, ...}
```
-----

```python
movie_sim_mat = {}
for user, movies in self.train_set.items():
    for m0 in movies:
        for m1 in movies:
            if m1 == m2:
                continue
            movie_sim_mat.setdefault(m1, {})
            movie_sim_mat[m1].setdefault(m2, 0)
            movie_sim_mat[m1][m2] += 1
```
```python
movie_sim_mat
{movie_0: {movie_1: count, ...}, ...}
```
-----


```python
for m1, related_movies in movie_sim_mat.items():
    for m2, count in related_movies.items():
        item_sim_mat[m1][m2] = count / math.sqrt(self.movie_popular[m1] * self.movie_popular[m2])
```
```python
movie_sim_mat
{movie_0: {movie_1: similarity, ...}, ...}
```
-----


```python
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
```
```python
[(movie, recommendation_value), ...]
```

