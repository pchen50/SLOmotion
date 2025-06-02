### Inserting a million rows
fake data modeling file : https://github.com/pchen50/SLOmotion/blob/main/fakeMillion.py 

## Write-Up
The above script will create around a million rows in the table. This script always creates 10,000 movies and 30,000 users. This is because currently our database is designed for users to rate just the top 250 movies on IMDb. Essentially we will always be the ones adding more movies to the database when we feel it is necessary which is why we kept our lowest number to be the number of movies. As our product grows there will likely be more users than movies which is why we set users to be 30,000. Then we created a right skewed distribution where most people have around 15 movie ratings but some people have much more movie ratings. Some users may be very into tracking their movies while others might just want to see what their friends are rating. Most users will most likely create an account and be active at the beginning and then slowly not rate as many movies which is why they would have an average of 15 movie ratings. This creates around 450,000 movie ratings. Additionally users can also create comments on other people's movie ratings. We modeled this part so that on average each movie rating has 1.13 comments. This is reasonable because adding comments on ratings is a side feature, not one of the main uses of this service so most move ratings would not have that many comments on them. However some ratings might become popular and get lots of comments on them from other users which is why the average is relatively low. This creates a totlal of 450-500k comments on movie ratings which is how we get around a million rows in our database.

### Performance Results

## endpoint 1: 




### Slowest endpoint
## explain queries

