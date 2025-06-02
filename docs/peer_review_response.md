# Peer Review Response
---

## Feedback 1: Rafael Pena 
### Code Review
- User.py
    - We decided to add a username field to the users table and enforced a unique constraint on it. Which allows each user to be identified by.
 
- Watchlist.py
    - We decided to keep the string-based status for now since it improved readability across the API. However, if it becomes an issue later on, then we can change it, but for now, since it looks cleaner, we choose to keep it like that.
    - We decided not to do the access control to get_watched and get_watchlist_movies since we decided not to do the public/private.
    - Added rating validation to post_movie_onto_watchlist(), the addtowatchlist model now uses field(ge=1, le=10) to make sure the rating is between 1 and 10. If the user submits an invalid rating, the api responds with a 422 validation error.

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
- Users.py
  - the get_users() endpoint returns all users with their IDs and names
  - The /users/login/{user_id} endpoint is implemented but at /user/login/{user_id} path
 
- Watchlist.py
  - The public/priate watchlist control is public to simplify the API and user experience
  - The debugging print statements have been removed

 - Movies.py
   - The error message in get_movies was updated.
   - The movie_id is consistently used as an integer type across all endpoints

- Health.py
  - the /health endpoint is implemented with proper database connectivity checks and table existence verification

- Auth.py
  - API key print statement has been removed to prevent security issues
  - Authentication is properly implemented using API key headers
  
### Schema/API Design
- movie table
    - standarized movie_id consistently
    - Added proper JSON response formatting for endpoints
    - Added more detailed error messages and fixed issues with certain messages
      
- users table
    - Added GET /users/users endpoint to list all users with IDs and names
    - username field has a unique constraint
      
- Comments Table
    - comments are linked to both movie and user for each rating
    - added error handling for comment endpoints
      
- Movie_ratings table
    - removed duplicate user_id and movie_id from request body
    - the movie_ratings table has standarized status values

- deleted watchlist and watchlist_movies tables

---

## Feedback 3: Sameer Nadeem
### Code Review
- Users.py
  - get_users() endpoint returns users with their IDs and names
  - /users/login/{user_id} endpoint is implemented at /user/login/{user_id} path
  - removed redundant integer casting of user_id
 
- Watchlist.py
  - debugging print statements removed
  - duplicate getting watchlist ID helper function not implemented, unnecessary
  - status values are string based still, change to integer based key values was not necessary

 - Movies.py
   - error messages in get_movies was updated to be clearer
   - movie_id is consistently used as an int across codebase
   - GET /movies/{movie_name} now returns proper JSON with movie_id key
  
- Recommended.py
  - get_recommend_movies function uses efficient SQL query with GROUP BY and COUNT to find most common genre in database

### Schema/API Design
- movie table
    -  GET /movies/{movie_name} now returns proper JSON with "movie_id" key
    -  don't need an additional movie detail endpoint as it would be too much effort to implement
    - 
- users table
    - added GET /user/users endpoint to list all users with their IDs and names
    - standardized to use user_id consistently across all endpoints
      
- Comments Table
    - added a GET comments endpoint
    - comments are linked to movie and user
      
- Movie_ratings table
    - Fixed PATCH endpoint to check user existence
    - removed user_id and movie_id duplicates
    - uses rating validation (1-10)
      
- deleted watchlist and watchlist_movies tables
