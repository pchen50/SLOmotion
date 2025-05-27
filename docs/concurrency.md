# Concurrency 
---
## 1. Dirty Read
- Dirty Reads occur when a tranasction reads data that has been modified by another transaction but hasn't been committed yet. 
- Example: 2 users try to update or read the same movie rating at the same time, user 1 updates the movie rating ```PATCH /watchlist/{user_id}/{movie_id}``` while user 2 requests user 1's watch list ```GET /watchlist/{user_id}/watched```. Without concurrency control, the second users transaction could read uncommitted changes made by the first user. This would be a dirty read and it could act on data that might be rolled back at a later time.
- To ensure that this does not happen, the db.engine.begin() wrapper makes sure that the update is wrapped in a transaction. PostgreSQL also uses a READ COMMITTED isolation level by default, preventing the possibility of dirty reads. 
### Sequence Diagram
<img width="433" alt="image" src="https://github.com/user-attachments/assets/8064e798-487d-4d6a-b9ad-f235494e2627" />

---
## 2. Non-Repeatable Read
- A non-repeatable read occurs when a transaction reads the same row twice and gets different data because another transaction modified it in the middle of the first transaction. 
- Example: User 1 reads a movie rating, calling the ```GET /watchlist/{user_id}/{movie_id}```. Before this transaction ends, another user (user 2) updates the movie rating using ```PATCH /watchlist/{user_id}/{movie_id}```. Still in the original transaction, user 1 reads the rating again but sees a different result.
- This doesn't happen because each endpoint function is wrapped using with db.engine.begin() as connection: and because users can only update their own ratings. 
### Sequence Diagram



---
## 3. Phantom Read
- A phantom read occurs when a transaction re-executtes a query that returns a set of rows, and gets a different set the second time because another transaction added or removed rows that match the query condition.
- Example: User 1 wants to see the list of watched movies, calling ```GET /watchlist/{user_id}/watched``` and sees 4 movies that are marked as "watched". However, before the transaction ends, another process adds a 5th movie with the "watched" status. If the original request reruns the same query before committing, it could now see 5 movies.
- This doesn't happen in our system because each API request runs in its own transaction. Queries are not re-run in the same transaction and only the owner of the watchlist can modify the data. 
### Sequence Diagram


