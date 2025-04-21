# Api specifications

1. **POST /users/login/{user_id}**  
   a. Description: Validate a user and start the session  
   b. Body:
      ```json
      {
        "user_id": "90138976",
        "password": "secret"
      }
      ```
   c. Returns: a token

2. **POST /watchlist/{user_id}/{movie_id}**  
   a. Description: Add a movie to the user's watchlist  
   b. Body:
      ```json
      {
        "movie_id": "tt0241527",
        "status": "want to watch",
        "rating": 9,
        "notes": "Magic",
        "mood_tags": ["fantasy", "adventure"]
      }
      ```
   c. Returns: It updates the watchlist LIST  
   d. Note: https://www.imdb.com/title/tt0241527/

3. **GET /watchlist/{user_id}/watched**  
   a. Description: Get any user's watchlist for movies they've watched  
   b. Body:
      ```json
      {
        "user_id": "3910876",
        "status": "watched"
      }
      ```
   c. Returns: a list of all movies on a user's watchlist  
   d. Example return:
      ```json
      [
        {
          "movie_id": "tt0241527",
          "status": "watched",
          "rating": 9,
          "notes": "Magic",
          "mood_tags": ["fantasy", "adventure"]
        },
        {
          "movie_id": "tt0117008",
          "status": "watched",
          "rating": 10,
          "notes": "Magic",
          "mood_tags": ["whimsical"]
        }
      ]
      ```

4. **PATCH /watchlist/{user_id}/{movie_id}**  
   a. Description: Edits a user's description/rating for a particular movie  
   b. Body:
      ```json
      {
        "user_id": "349103",
        "movie_id": "tt1517268",
        "Title": "Barbie",
        "status": "watched",
        "rating": 8
      }
      ```
   c. Returns: A confirmation that the movie description was changed  
   d. Example return:
      ```json
      {"message": "Successfully updated!"}
      ```

5. **GET /watchlist/{user_id}/statistics**  
   a. Description: Generate viewing statistics for the user's most watched genres and average ratings  
   b. Body:
      ```json
      {
        "user_id": "8239012",
        "average_rating": "7.2",
        "most_common_genres": ["action", "comedy"],
        "number_watched": 22
      }
      ```
   c. Returns: The user's list of statistics about the movies they have rated

6. **GET /recommended_movies/{user_id}**  
   a. Description: Creates a list of the recommended movies based on the user's preferences.  
   b. Body:
      ```json
      [
        {
          "movie_id": "tt1517268",
          "Title": "Gladiator",
          "rating": "9.8",
          "genre": "action"
        },
        {
          "movie_id": "tt1417298",
          "Title": "Good Will Hunting",
          "rating": "9.7",
          "genre": "drama"
        }
      ]
      ```
   c. Returns: A list of top recommended movies for the user

7. **DELETE /watchlist/{user_id}/{movie_id}**  
   a. Description: Removes a specified movie from the user's watchlist  
   b. Body: Empty  
   c. Returns: Success status code (204 No Content) or deletion message  
   d. Example return:
      ```json
      {"Message": "Successfully removed movie."}
      ```

8. **GET /ratings/{movie_id}**  
   a. Description: Retrieves a list of user ratings for a specified movie  
   b. Body: Empty  
   c. Returns: List of user ratings  
   d. Example return:
      ```json
      [
        {"user_id": 1231231, "rating": 7},
        {"user_id": 3213213, "rating": 8}
      ]
      ```

9. **POST /watchlist/{user_id}/{movie_id}/{user2_id}/comment**  
   a. Description: Adds a comment under a specific user's movie rating  
   b. Body:
      ```json
      {
        "User_id": "1391810",
        "User2_id": "381739",
        "Movie_id": "tt1517268",
        "comment": "completely agree with this rating"
      }
      ```
   c. Returns: A message saying that the comment was added  
   d. Example return:
      ```json
      {"message": "comment successfully added"}
      ```

---

# 3 Distinct Example Flows

## 1. Watchlist User Makes a Comment Example Flow
Bob just finished watching *Good Will Hunting* for a second time and had some thoughts about the movie. He wants to leave a comment on his friend Joe's watchlist.

- Bob calls `GET /watchlist/876543` to see Joe’s recently watched list.
- He sees *Good Will Hunting* under `movie_id tt1417298`.
- He then calls `GET /watchlist/876543/tt1417298` to view the movie entry.
- Bob submits a comment with:
  ```json
  {
    "comment": "I really connected with the character Will in the movie."
  }
  ```
- Request: `POST /watchlist/876543/tt1417298/1391810/comment`
- Server response:
  ```json
  { "message": "Comment added." }
  ```

## 2. Watchlist User Looks for a Movie to Watch Example Flow
Alice finishes watching *Barbie* and updates its status in her watchlist. She then checks Bob's watchlist and finally gets new recommendations for herself.

- Alice calls `PATCH /watchlist/456219/tt1517268`
  ```json
  {
    "user_id": "456219",
    "movie_id": "tt1517268",
    "status": "watched",
    "rating": 8
  }
  ```
- Server response:
  ```json
  { "message": "Successfully updated!" }
  ```
- Alice calls `GET /watchlist/876543/watched`
  ```json
  {
    "user_id": "876543",
    "status": "watched"
  }
  ```
- Server response:
 ```json
 [
   {
      "movie_id": "tt1517268",
      "title": "Gladiator",
      "status": "watched",
      "rating": "9.8",
      "genre": "action"
    },
    {
      "movie_id": "tt1417298",
      "title": "Good Will Hunting",
      "status": "watched",
      "rating": "9.7",
      "genre": "drama"
    }
 ]
``` 
- She then calls `GET /recommended_movies/456219` to receive personalized recommendations.

## 3. Watchlist User Adds and Removes Movies Example Flow
Eve gets a recommendation to watch *A Minecraft Movie*, but later changes her mind.

- Eve calls `GET /ratings/tt3566834` and sees strong user ratings.
- She adds the movie using `POST /watchlist/376541/tt3566834`
  ```json
  {
    "user_id": "376541",
    "movie_id": "tt3566834",
    "status": "want to watch"
  }
  ```
- After watching, Eve decides to remove it using:
  `DELETE /watchlist/376541/tt3566834`
- Server responds:
  ```json
  { "Message": "Successfully removed movie." }
  ```


