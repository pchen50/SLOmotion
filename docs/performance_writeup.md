### Inserting a million rows
fake data modeling file : https://github.com/pchen50/SLOmotion/blob/main/fakeMillion.py 

## Write-Up
The above script will create around a million rows in the table. This script always creates 10,000 movies and 30,000 users. This is because currently our database is designed for users to rate just the top 250 movies on IMDb. Essentially we will always be the ones adding more movies to the database when we feel it is necessary which is why we kept our lowest number to be the number of movies. As our product grows there will likely be more users than movies which is why we set users to be 30,000. Then we created a right skewed distribution where most people have around 15 movie ratings but some people have much more movie ratings. Some users may be very into tracking their movies while others might just want to see what their friends are rating. Most users will most likely create an account and be active at the beginning and then slowly not rate as many movies which is why they would have an average of 15 movie ratings. This creates around 450,000 movie ratings. Additionally users can also create comments on other people's movie ratings. We modeled this part so that on average each movie rating has 1.13 comments. This is reasonable because adding comments on ratings is a side feature, not one of the main uses of this service so most move ratings would not have that many comments on them. However some ratings might become popular and get lots of comments on them from other users which is why the average is relatively low. This creates a totlal of 450-500k comments on movie ratings which is how we get around a million rows in our database.

### Performance Results

## endpoint 1: post /user/ create user
```sql
INSERT INTO users (name, username)
VALUES (:customer_name, :username)
RETURNING id
```
This took 9 ms

## endpoint 2: get /user/lookup/{username} get user by username
```sql
SELECT id FROM users
WHERE username = :username
```

This took 6 ms

## endpoint 3 get /user/login/{user_id} "login" return name and username from user id
```sql
SELECT id AS user_id, name, username
FROM users
WHERE id = :user_id
```
This took 9 ms

## endpoint 4 get /watchlist/{user_id}/stats get user stats
```sql
SELECT movie_id, user_id, notes, rating, status, name, genre
FROM movie_ratings
JOIN movies on movies.id = movie_ratings.movie_id
WHERE user_id = :user_id
ORDER BY movie_ratings.id DESC (used user_id = 3789)
```
This took 30 ms

## endpoint 5 get /watchlist/{user_id}/watched get user's watched movies
```sql
SELECT movie_id, movies.name as name, movie_ratings.status as status, movie_ratings.rating as rating, movies.genre as genre
FROM movie_ratings
JOIN movies on movie_ratings.movie_id = movies.id
WHERE user_id = :user_id and status = 'watched' (used user_id = 1297)
```
This took 28 ms

## endpoint 6 get /watchlist/{user_id} get everything on a user's watchlist
```sql
SELECT movie_id, movies.name as name, movie_ratings.status as status, movie_ratings.rating as rating, movies.genre as genre
FROM movie_ratings
JOIN movies on movie_ratings.movie_id = movies.id
WHERE user_id = :user_id (used user_id = 29997)
```
This took 26 ms 

## endpoint 7 get /watchlist/{user_id}/{movie_id} get a user's rating for a movie
```sql
SELECT movie_id, user_id, notes, rating, status
FROM movie_ratings
WHERE user_id = :user_id AND movie_id = :movie_id (used user_id = 105 and movie_id = 8446)
```
This took 2 ms

## endpoint 8 patch /watchlist/{user_id}/{movie_id} update a user's rating for a movie
```sql
UPDATE movie_ratings
SET {", ".join(fields)}
WHERE user_id = :user_id AND movie_id = :movie_id
RETURNING id
```
for this one we ran
```sql
UPDATE movie_ratings
SET rating = 2
WHERE user_id = 105 AND movie_id = 8446 
RETURNING id
```
This took 21 ms

## endpoint 9 post /watchlist/{user_id}/{movie_id} post a new user's rating for a movie
This had multiple queries
```sql
SELECT id 
FROM movie_ratings
WHERE user_id = 21 AND movie_id = 2
```
This took 2 ms, then
```sql
INSERT INTO movie_ratings (user_id, movie_id, notes, rating, status)
VALUES (21, 2, "N/A", null, "want to watch")
RETURNING id
```
This took 11 ms
So the endpoint overall took 13 ms

## endpoint 10 DELETE /watchlist/{user_id}/{movie_id} delete's a user's movie rating
This also has multiple queries in the endpoint
```sql
SELECT id 
FROM movie_ratings
WHERE user_id = 21 AND movie_id = 2
```
Took 3 ms
```sql
DELETE FROM comments
WHERE user_id = 21 AND movie_id = 2
```
This took 40 ms
```sql
DELETE FROM movie_ratings
WHERE id = 439826 (this is the movie rating id that we got from the first select query)
```
This took 4 ms. Overall the whole endpoint took 47 ms

## endpoint 11 POST /watchlist/{user_id}/{movie_id}/{user2_id}/comment post a comment onto a existing movie rating
This also has 2 queries
```sql
SELECT 1
FROM movie_ratings
WHERE user_id = 122 AND movie_id = 2396
```
This took 2 ms
```sql
INSERT INTO comments (commenter_user_id, user_id, movie_id, comment_text)
VALUES (38, 122, 2396, 'whole heartedly agree with you')
```
This took 18 ms. Overall the whole endpoint took 20 ms

## endpoint 12 GET /watchlist/{user_id}/{movie_id}/comments get the comments on a movie rating
```sql
SELECT c.commenter_user_id, u.username AS commenter_username, c.comment_text
FROM comments c
JOIN users u ON c.commenter_user_id = u.id
WHERE c.user_id = :user_id AND c.movie_id = :movie_id (used user_id = 122 and movie_id = 2396)
ORDER BY c.id DESC
```
This took 36 ms

## endpoint 13 GET /recommended_movies/{user_id} get recommended movies for a user
This endpoint has 2 queries
```sql
SELECT m.genre
FROM movie_ratings mr
JOIN movies m ON mr.movie_id = m.id
WHERE mr.user_id = :user_id (used user_id 1343)
GROUP BY m.genre
ORDER BY COUNT(*) DESC
LIMIT 1
```
This took 36 ms

```sql
SELECT m.id AS movie_id, m.name, m.genre
FROM movies m
WHERE m.genre = 'consumer'
AND m.id NOT IN (
    SELECT movie_id
    FROM movie_ratings
    WHERE user_id = 1343
)
ORDER BY RANDOM()
LIMIT 5
```
This took 35 ms
Overall this endpoint took 71 ms

## endpoint 14 GET /movies/{movie_name} get a movie's movie_id
```sql
SELECT movies.id 
FROM movies 
WHERE lower(movies.name) LIKE lower('Company at') AND movies.year = 2006
```
This took 6 ms

## endpoint 15 GET /movies/ratings/{movie_id} get all the ratings for a movie
```sql
SELECT user_id, rating
FROM movie_ratings
WHERE movie_id = 12
```
This took 11 ms

# Slowest endpoints
1. The slowest endpoint was endpoint 13 which had two queries that each took around 30 ms to complete.
1. The second slowest endpoint was endpoint 10 which took 47 ms.
1. The third slowest endpoint was endpoing 12 which took 36 ms. 

## explain queries

### second query
(We optimized the second query of the endpoint first which is why it is shown first here)
```sql
EXPLAIN ANALYZE
SELECT m.id AS movie_id, m.name, m.genre
FROM movies m
WHERE m.genre = 'consumer'
AND m.id NOT IN (
    SELECT movie_id
    FROM movie_ratings
    WHERE user_id = 1343
)
ORDER BY RANDOM()
LIMIT 5
```
### Query plan
```
Limit  (cost=9830.42..9830.43 rows=5 width=34) (actual time=24.886..24.887 rows=5 loops=1)
  ->  Sort  (cost=9830.42..9830.43 rows=5 width=34) (actual time=24.884..24.885 rows=5 loops=1)
        Sort Key: (random())
        Sort Method: top-N heapsort  Memory: 25kB
        ->  Seq Scan on movies m  (cost=9603.35..9830.36 rows=5 width=34) (actual time=23.307..24.761 rows=12 loops=1)
"              Filter: ((NOT (ANY (id = (hashed SubPlan 1).col1))) AND ((genre)::text = 'consumer'::text))"
              Rows Removed by Filter: 9988
              SubPlan 1
                ->  Index Only Scan using movie_ratings_movie_id_user_id_key on movie_ratings  (cost=0.42..9603.30 rows=19 width=4) (actual time=0.625..22.887 rows=17 loops=1)
                      Index Cond: (user_id = 1343)
                      Heap Fetches: 0
Planning Time: 0.968 ms
Execution Time: 25.064 ms
```

Looking at this it's looking like this is doing a sequential scan on all 10,000 movies in the database. Given that we want to only be selecting at random from the movies that match the given genre, we should create an index by genre for the movies table.

creating the index:
```sql 
CREATE INDEX movies_genre_idx ON movies (genre)
```

rerunning explain analyze:
```
Limit  (cost=9647.88..9647.89 rows=5 width=34) (actual time=24.470..24.472 rows=5 loops=1)
  ->  Sort  (cost=9647.88..9647.89 rows=5 width=34) (actual time=24.469..24.469 rows=5 loops=1)
        Sort Key: (random())
        Sort Method: top-N heapsort  Memory: 25kB
        ->  Index Scan using movies_genre_idx on movies m  (cost=9603.63..9647.82 rows=5 width=34) (actual time=24.427..24.444 rows=12 loops=1)
"              Index Cond: ((genre)::text = 'consumer'::text)"
              Filter: (NOT (ANY (id = (hashed SubPlan 1).col1)))
              Rows Removed by Filter: 1
              SubPlan 1
                ->  Index Only Scan using movie_ratings_movie_id_user_id_key on movie_ratings  (cost=0.42..9603.30 rows=19 width=4) (actual time=0.557..23.762 rows=17 loops=1)
                      Index Cond: (user_id = 1343)
                      Heap Fetches: 0
Planning Time: 1.144 ms
Execution Time: 24.652 ms
```

This did not decrease the execution time as much as we had hoped. Another thing that stands out is the subplan which is using an index on both movie_id and user_id. It might be faster if instead the index was jsut on the user_id itself in the movie_ratings table which would help with filtering out movies of that genre that the user has already watched since we won't know ahead of time those movie_ids.

Creating an index on user_id: 
```sql 
CREATE INDEX movie_ratings_user_idx ON movie_ratings (user_id)
```

rerunning explain analyze:
```
Limit  (cost=42.58..42.60 rows=5 width=34) (actual time=0.836..0.837 rows=5 loops=1)
  ->  Sort  (cost=42.58..42.60 rows=5 width=34) (actual time=0.835..0.836 rows=5 loops=1)
        Sort Key: (random())
        Sort Method: top-N heapsort  Memory: 25kB
        ->  Bitmap Heap Scan on movies m  (cost=13.17..42.52 rows=5 width=34) (actual time=0.613..0.676 rows=12 loops=1)
"              Recheck Cond: ((genre)::text = 'consumer'::text)"
              Filter: (NOT (ANY (id = (hashed SubPlan 1).col1)))
              Rows Removed by Filter: 1
              Heap Blocks: exact=11
              ->  Bitmap Index Scan on movies_genre_idx  (cost=0.00..4.36 rows=10 width=0) (actual time=0.085..0.086 rows=13 loops=1)
"                    Index Cond: ((genre)::text = 'consumer'::text)"
              SubPlan 1
                ->  Index Scan using movie_ratings_user_idx on movie_ratings  (cost=0.42..8.76 rows=19 width=4) (actual time=0.420..0.423 rows=17 loops=1)
                      Index Cond: (user_id = 1343)
Planning Time: 0.955 ms
Execution Time: 1.296 ms
```
This significantly dropped down the execution time (over 20 milliseconds) and is now at a much more reasonable time for finding movies in a particular genre that aren't already on the user's watchlist.

## first query
Running explain query; this explain analyze was done before the indexes were added to fix the second query above.
```sql
EXPLAIN ANALYZE
SELECT m.genre
FROM movie_ratings mr
JOIN movies m ON mr.movie_id = m.id
WHERE mr.user_id = :user_id (used user_id 1343)
GROUP BY m.genre
ORDER BY COUNT(*) DESC
LIMIT 1
```
## Query plan
```
Limit  (cost=9737.88..9737.88 rows=1 width=14) (actual time=22.982..22.983 rows=1 loops=1)
  ->  Sort  (cost=9737.88..9737.93 rows=19 width=14) (actual time=22.981..22.982 rows=1 loops=1)
        Sort Key: (count(*)) DESC
        Sort Method: top-N heapsort  Memory: 25kB
        ->  GroupAggregate  (cost=9737.45..9737.78 rows=19 width=14) (actual time=22.892..22.899 rows=17 loops=1)
              Group Key: m.genre
              ->  Sort  (cost=9737.45..9737.50 rows=19 width=6) (actual time=22.883..22.885 rows=17 loops=1)
                    Sort Key: m.genre
                    Sort Method: quicksort  Memory: 25kB
                    ->  Nested Loop  (cost=0.71..9737.05 rows=19 width=6) (actual time=0.367..22.777 rows=17 loops=1)
                          ->  Index Only Scan using movie_ratings_movie_id_user_id_key on movie_ratings mr  (cost=0.42..9603.30 rows=19 width=4) (actual time=0.328..22.468 rows=17 loops=1)
                                Index Cond: (user_id = 1343)
                                Heap Fetches: 0
                          ->  Index Scan using movies_pkey on movies m  (cost=0.29..7.04 rows=1 width=10) (actual time=0.017..0.017 rows=1 loops=17)
                                Index Cond: (id = mr.movie_id)
Planning Time: 1.873 ms
Execution Time: 23.188 ms
```
Looking at this, the index scan on movie_ratings was using both the user_id and movie_id. However this would prove to be useless since there are no movie_ids provided. After we implemented the index on user_id on movies, this dropped the time for this query as well.

Rerunning explain analyze:
```
Limit  (cost=143.34..143.35 rows=1 width=14) (actual time=0.389..0.393 rows=1 loops=1)
  ->  Sort  (cost=143.34..143.39 rows=19 width=14) (actual time=0.386..0.388 rows=1 loops=1)
        Sort Key: (count(*)) DESC
        Sort Method: top-N heapsort  Memory: 25kB
        ->  GroupAggregate  (cost=142.92..143.25 rows=19 width=14) (actual time=0.335..0.356 rows=17 loops=1)
              Group Key: m.genre
              ->  Sort  (cost=142.92..142.96 rows=19 width=6) (actual time=0.284..0.289 rows=17 loops=1)
                    Sort Key: m.genre
                    Sort Method: quicksort  Memory: 25kB
                    ->  Nested Loop  (cost=0.71..142.51 rows=19 width=6) (actual time=0.068..0.234 rows=17 loops=1)
                          ->  Index Scan using movie_ratings_user_idx on movie_ratings mr  (cost=0.42..8.76 rows=19 width=4) (actual time=0.046..0.061 rows=17 loops=1)
                                Index Cond: (user_id = 1343)
                          ->  Index Scan using movies_pkey on movies m  (cost=0.29..7.04 rows=1 width=10) (actual time=0.009..0.009 rows=1 loops=17)
                                Index Cond: (id = mr.movie_id)
Planning Time: 0.841 ms
Execution Time: 0.495 ms
```
This is a much faster time than we had before.