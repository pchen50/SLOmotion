# Peer Review Response
---

## Feedback 1: Rafael Pena 
### Code Review
- 
### Schema/API Design
- movie table
    - added a year column to the movies table to help with differentiating between movies that have the same name and genre
- users table
    - added a username column to the users table and set a uniqueness constraint on this column so that there the user id isn't the only way to differentiate users
- Comments Table
    - added foreign key constraint on commenter_user_id column
    - added uniqueness constraint to commenter_user_id, user_id, movie_id
    - edited all columns to ensure none were nullable
    - since there is no endpoint to delete users or movies did not set up on delete cascade for any foreign key references
- Movie_ratings table
    - changed ratings to be float instead of integers
    - added uniqueness constraint on (movie_id, user_id)
    - made sure movie_id and user_id are not nullable
- deleted watchlists and watchlist_movies table

---

## Feedback 2: Megan Robinson
### Code Review
- 
### Schema/API Design
- 

---

## Feedback 3: Sameer Nadeem
### Code Review
- 
### Schema/API Design
- deleted watchlist and watchlist_movies tables
