# API specifications

---

 POST /users/login/{user_id}
Description: Validate a user and start the session
 Body:
{
  "user_id": “90138976",
  "password": "secret"
}
Returns: a token

 POST /watchlist/{user_id}/{movie_id}
Description: Add a movie to the user’s watchlist
Body:
{
  "movie_id": "tt0241527", (used an actual IMDb ID)
  "status": "want to watch",
  "rating": 9,
  "notes": "Magic",
  "mood_tags": ["fantasy", "adventure"]
}
Returns: It updates the watchlist LIST
Note: https://www.imdb.com/title/tt0241527/
 GET /watchlist/{user_id}/watched
Description: Get any user’s watchlist for movies they’ve watched
Body: 
{
 “user_id”: “3910876”
 “status”: “watched
 }
Returns: a list of all movies on a user’s watchlist
Example return: [
   {
 			 "movie_id": "tt0241527", (used an actual IMDb ID)
 			 "status": "watched",
 			 "rating": 9,
  "notes": "Magic",
 			 "mood_tags": ["fantasy", "adventure"]
},
{
 			 "movie_id": "tt0117008", (used an actual IMDb ID)
 			 "status": "watched",
 			 "rating": 10,
  "notes": "Magic",
 			 "mood_tags": ["whimsical”]
}
]
 PATCH /watchlist/{user_id}/{movie_id}
Edits a user’s description/rating for a particular movie
Body:
{
  “user_id”: “349103”,
  “movie_id”: “tt1517268”,
“Title”: “Barbie”
  “status”: “watched”
  “rating”: 8
}
Returns: returns a confirmation that the movie description was changed
Example return
{“message”: “Successfully updated!”}
  GET /watchlist/{user_id}/statistics
Generate viewing statistics for the user’s most watched genres and average ratings
Body:
{
  “user_id”: “8239012”,
  “average_rating”: “7.2”,
  “most_common_genres”: [“action”, “comedy”],
“number_watched”: 22
}
Returns: the user’s list of statistics about the movies they have rated
GET /recommended_movies/{user_id}
Creates a list of the recommended movies based on the user’s preferences.
Body:
{
  “movie_id”: “tt1517268”,
 “Title”: “Gladiator”,
  “rating”: “9.8”,
  “genre”: “action”
},
{
 “movie_id”: “tt1417298”,
 “Title”: “Good Will Hunting”,
  “rating”: “9.7”,
  “genre”: “drama”,

}
Returns a list of top recommended movies for the user.
 
 DELETE /watchlist/{user_id}/{movie_id}
Removes a specified movie from the user’s watchlist.
Body: Empty
Returns: Returns a success status code response (204 No Content) or message is successfully deleted.
Example return:
		{ 	
		“Message”: “Successfully removed movie.”
		}
		
 GET /ratings/{movie_id}
Retrieves a list of user ratings for a specified movie.
Body: Empty
Returns: If the movie exists, returns a list of user ratings.
Example return:
[
{“user_id”: 1231231, “rating” : 7},
{“user_id”: 3213213, “rating” : 8)
]
POST /watchlist/{user_id}/{movie_id}/{user2_id}/comment
Adds a comment under a specific user’s movie rating
body
{
 “User_id”: “1391810”,
 “User2_id”: “381739”, (the person adding the comment)
 “Movie_id”: “tt1517268”,
 “comment”: “completely agree with this rating”}
Returns a message saying that the comment was added
{“message”: “comment successfully added”}
 
---
# 3 Distinct Example Flows
---
Watchlist User Makes a Comment Example Flow
	Bob just finished watching Good Will Hunting for a second time and had some thoughts about the movie, so he wanted to add some comments he had on the film. First, Bob requests to go to his friend’s watchlist using GET /watchlist/876543, where he sees that Good Will Hunting is listed under his friend Joe’s recently watched movies, under movie_id tt1417298. To leave a comment under the movie, 
Bob first calls GET/watchlist/876543 where he sees the list of movies Joe has watched
Then Bob clicks on the movie he wants to comment on, calling GET/watchlist/876543/tt1417298 to select the movie Good Will Hunting that he wants to leave a comment on
Bob then decides to leave a comment, calling POST /watchlist/876543/tt1417298/1391810/comment 
In the body of the request, Bob sends: { “comment”: “I really connected with the character Will in the movie.” }
Bob hits the “Finish Comment” button, and the server responds to Bob with: {“message”: “Comment added.” }
Now, whenever Bob, Joe, or their friends check the movie Good Will Hunting under Joe’s watchlist, they will see Bob’s comment. 

Watchlist User looks for a movie to watch, example flow
Alice finishes watching the Barbie movie and updates the status from ‘want to watch’ to ‘watched’. She does this by calling  PATCH /watchlist/456219/{tt1517268. She has a lot of free time but is unsure of what to watch next, so she decides to check her friend’s (Bob) watchlist by calling  GET /watchlist/876543/watched. After viewing Bob’s watchlist and ratings, she realizes Bob has horrible taste and wants to see what is recommended for her. She calls  GET /recommended_movies/filmcriticalice29.

Alice calls  PATCH /watchlist/456219/tt1517268 
The body is 
{
  “user_id”: “456219”,
  “movie_id”: “tt1517268”,
  “status”: “watched”
  “rating”: 8
}
The server responds with {“message”: “Successfully updated!”}
Alice calls GET /watchlist/876543/watched  to get Bob’s list
The body {“user_id”: “876543”,
“status”: “watched”}
The server responds with the list of all the ratings Bob has given for movies he has marked as watched.
Alice then decides to call GET /recommended_movies/456219
The server responds to that by returning another list of movies generated by the preferences Alice indicated through her previous movie ratings.

Watchlist User adds and removes movies from their watchlist example flow
Eve is tired of watching movies with no plot and asks Bob for a recommendation. He suggests to give A Minecraft Movie a chance. Eve then checks the user ratings for the show by using GET /ratings/tt3566834, and sees that it is rated high, and wants to give it a try. To track it, she requests to add the movie into her watchlist under the status "want to watch" by calling POST /watchlist/EvesMovies/tt3566834. After reviewing the movie, Eve doesn't get the hype around it. She then decides it isn't even worth rating and having in her watchlist, and requests to remove the movie by calling DELETE /watchlist/376541/tt3566834. 

Eve calls GET /ratings/tt3566834
The server responds with a list of user ratings for the movie.
Eve calls POST /watchlist/376541/tt3566834 and sets the request parameter for status to “want to watch”
Eve then, calls DELETE /watchlist/376541/tt3566834.
The server responds with a message confirming the deletion.


