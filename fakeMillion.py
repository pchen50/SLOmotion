import sqlalchemy
import os
from dotenv import load_dotenv
from faker import Faker
import numpy as np
import random

def database_connection_url():
    load_dotenv("default.env")
    uri: str = os.environ.get("POSTGRES_URI")
    return uri

engine = sqlalchemy.create_engine(database_connection_url(), use_insertmanyvalues=True)

with engine.begin() as conn:
    conn.execute(sqlalchemy.text("""
    DROP TABLE IF EXISTS comments;
    DROP TABLE IF EXISTS movie_ratings;
    DROP TABLE IF EXISTS users;
    DROP TABLE IF EXISTS movies;

    CREATE TABLE 
        movies (
            id int generated always as identity not null PRIMARY KEY,
            name varchar not null,
            genre varchar not null,
            year int not null
        );

    CREATE TABLE
    users (
        id int generated always as identity not null PRIMARY KEY,
        name varchar not null,
        username varchar(100) unique not null
    );    
        
    CREATE TABLE
    comments (
        id int generated always as identity not null PRIMARY KEY,
        commenter_user_id int not null references users(id), 
        user_id int not null references users(id),
        movie_id int not null references movies(id),
        comment_text varchar not null,
        UNIQUE(commenter_user_id, user_id, movie_id)
    );
                                 
    CREATE TABLE
    movie_ratings (
        id int generated always as identity not null PRIMARY KEY,
        movie_id int not null references movies(id),
        user_id int not null references users(id),
        notes varchar,
        rating float,
        status varchar,
        UNIQUE(movie_id, user_id)
    );
    """))


fake = Faker()
rng = np.random.default_rng()
# inserting 10000 movies into the movies table
with engine.begin() as conn:
    for i in range(10000):
        name = fake.sentence(nb_words=3).rstrip('.')
        genre = fake.word()
        year = rng.integers(1920, 2026)
        conn.execute(sqlalchemy.text(
            """INSERT INTO movies (name,genre,year) VALUES (:name,:genre,:year)"""
        ),{"name": name, "genre": genre, "year": year})
    
num_users = 30000
ratings_sample_distribution = rng.negative_binomial(2.0, 0.12, num_users)

num_ratings = 0

all_ratings = []
all_full_ratings = []
# create fake users with fake names and usernames
with engine.begin() as conn:
    print("creating fake posters...")
    for i in range(num_users):
        ratings = []
        if (i % 1000 == 0):
            print(i)
        
        name = fake.first_name()
        username = fake.unique.email()

        user_id = conn.execute(sqlalchemy.text("""
        INSERT INTO users (name,username) VALUES (:name,:username) RETURNING id;
        """), {"username": username, "name": name,}).scalar_one()

        # creating fake movie ratings
        # making sure that all users will have less than 10000 ratings since that
        num_posts = min(ratings_sample_distribution[i], 10000)
        movie_ids = rng.choice(10000, size=num_posts, replace=False)
        for j in range(num_posts):
            num_ratings += 1
            all_ratings.append((movie_ids[j] + 1, user_id))
            ratings.append({
                "movie_id": movie_ids[j] + 1,
                "user_id": user_id,
                "notes": fake.text(),
                "rating": round(random.uniform(0,10.0),2),
                "status": fake.random_element(elements=("watched", "want to watch", "watching"))
            })

        all_full_ratings += ratings
        
        if len(all_full_ratings) > 5000:
            conn.execute(sqlalchemy.text("""
                INSERT INTO movie_ratings (movie_id, user_id, notes, rating, status) 
                VALUES (:movie_id, :user_id, :notes, :rating, :status);
                """), all_full_ratings)
            all_full_ratings = []

    if len(all_full_ratings) > 0:
        conn.execute(sqlalchemy.text("""
            INSERT INTO movie_ratings (movie_id, user_id, notes, rating, status) 
            VALUES (:movie_id, :user_id, :notes, :rating, :status);
            """), all_full_ratings)
        all_full_ratings = []
    print("total ratings: ", num_ratings)

# creating comments for each rating
num_comments_per_rating = rng.poisson(lam=1.13, size=num_ratings)
tot_comments = 0
all_comments = []

for i in range(len(num_comments_per_rating)):
    comments = []
    num_comments = num_comments_per_rating[i]
    commenters = rng.choice(30000, size=num_comments, replace=False)
    for j in range(num_comments):
        tot_comments += 1
        comments.append(
            {
                "commenter_user_id": commenters[j] + 1,
                "user_id": all_ratings[i][1],
                "movie_id": all_ratings[i][0],
                "comment_text": fake.text()
            }
        )
        
    all_comments += comments
        
    if len(all_comments) > 5000:
        with engine.begin() as conn:
            conn.execute(sqlalchemy.text("""
            INSERT INTO comments (commenter_user_id, user_id, movie_id, comment_text) 
            VALUES (:commenter_user_id, :user_id,:movie_id, :comment_text);
            """), all_comments)
            all_comments = []
if len(all_comments) > 0:
    with engine.begin() as conn:
        conn.execute(sqlalchemy.text("""
        INSERT INTO comments (commenter_user_id, user_id, movie_id, comment_text) 
        VALUES (:commenter_user_id, :user_id,:movie_id, :comment_text);
        """), all_comments)
        all_comments = []
print("total comments: ", tot_comments)

print(f"Total rows estimate: movies=10000, users={num_users}, ratings={num_ratings}, comments={tot_comments}")
print(f"Total = {10000 + num_users + num_ratings + tot_comments}")


'''
This script will create around a million rows in the table. This script always creates 10,000 movies and 30,000 users. This is because 
currently our database is designed for users to rate just the top 250 movies on IMDb.
Essentially we will always be the ones adding more movies to the database when we feel it is necessary which is why we kept our lowest number
to be the number of movies. As our product grows there will likely be more users than movies which is why we set users to be 30,000.
Then we created a right skewed distribution where most people have around 15 movie ratings but some people have much more movie ratings.
Some users may be very into tracking their movies while others might just want to see what their friends are rating. Most users will most likely
create an account and be active at the beginning and then slowly not rate as many movies which is why they would have an average of 15 movie ratings.
This creates around 450,000 movie ratings. Additionally users can also create comments on other people's movie ratings.
We modeled this part so that on average each movie rating has 1.13 comments. This is reasonable because adding comments on ratings is
a side feature, not one of the main uses of this service so most move ratings would not have that many comments on them. However some
ratings might become popular and get lots of comments on them from other users which is why the average is relatively low. This creates a totlal of 450-500k
comments on movie ratings which is how we get around a million rows in our database.
'''