# User Stories and Exceptions
---

## Rachana
1.As a college student, I want to be able to see top rated movies, so I can easily get recommendations on what to watch next.
 ---
  *Exception:* Unable to show the top movies.
  If a user wants to see the top movies at the time and it’s unable to pull the top movies, it’ll show an error and will ask the user to check at a later time
2. As a movie critic, I want to be able to add detailed notes on the movies I watch so I can refer back to my original opinions.
 ---
  *Exception:* The movie critic writes an extremely large amount that can’t be stored.
  If someone writes too much in the notes section (past the limit), it’ll show an error asking them to edit their comment to fit the word limit.
3. As an avid movie watcher, I want to be able to store my movie ratings on a personal account online so everything is organized.
 ---
  *Exception:* the user enters the wrong password
  If a user is unable to log into their account, it’ll tell the user that they entered a wrong password and will ask them to re enter their password.


## Julianne
1. As a data nerd, I want to see statistics about my habits, so that I can analyze my viewing trends
   ---
  *Exception:* Analytics failed to make
  If there’s an issue generating the user’s movie stats, it will notify the user to refresh the page or try again later,
3. As a friend, I want to leave comments on someone else’s shared movie list, so that I can recommend or comment on the movies they added. 
   ---
  *Exception:*  Not logged in or doesn’t have comment permissions
  If a user tries to leave a comment without being logged in or without permission, they will be notified to log in or notified that commenting is disabled for that list. 
4. As a mood-based viewer, I want to tag movies with moods (for example, “ emotional” or “feel-good”), so that I can pick what to watch based on how I’m feeling.
   ---
  *Exception:*  User enters an invalid tag
  If the user types a tag that doesn’t meet the format or the length requirements, the system will suggest valid tags or allow them to create a new one that fits the requirements. 

## Phillip
1. As a movie enthusiast, I want to create a detailed profile that includes my personal scores, stats, and favorite genres so that I can showcase my watch history and share my movie list with others.
 ---
  *Exception:*  User enters invalid score 
  If a user enters a score outside the range (e.g. “11/10”, when the max is 10), it should result in an invalid input, and prompt the user to adjust it.
2. As a social user, I want to view other users' watchlists, so I can discover new movies based on their suggestions.
 ---
  *Exception:*  User views another’s private watchlist 
  If a user restricts access to their watchlist, the list will be hidden from outside viewers.
3. As an indecisive movie watcher, I want to add and remove movies from my watchlist so that I can keep my list updated.
 ---
  *Exception:*  User attempts to add/remove a movie title that is nonexistent
  If a user enters a movie that is not recognized by the database, it will prompt the user to enter the movie title again. 

## Noah
1. As a movie watcher, I want to filter my movies based on their genre so that I can find something that matches my taste.
 ---
  *Exception:* genre filter returns no results
  If no movies match the selected genre filter, the system will notify the user and suggest another related genre.
2. As a user that wants different visual effects available, I want the site to have a dark mode and different color options to customize my site.
 ---
  *Exception:* Color features not loading correctly.
  If the color settings fail to update, the user will be notified and directed to a help page while the system reloads the default settings.
3. As a bilingual user, I want to view movie titles and descriptions in another language to better understand what I am watching.
 ---
  *Exception:*  Translation not available. 
If the translation is not available, the site will let the user know what languages are available and default back to English. 


