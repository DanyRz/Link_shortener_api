****Api for creating short links****

**What it does:**

This project provides an API for shortening long links.
User can provide a link, that he wants to shorten, and get a randomly generated short version of it, that redirects to the original.
User can register, login, logout, update his credentials, view them and delete his account. Also, he is able to create short links, view them and delete, if they belong to him. All this actions except for registration and login require authorisation, that utilises hashed password and JWT tokens. Tokens can be refreshed.

**Instances:**

There are two - User and Link.
User has his id, username, his links and hashed password stored in database.
As for Link - it has in database it's id, long(original) wersion, short version and owner_id, which ties it to it's owner.

**How to run:**

1. Download the files to a directory
2. In directory, type from console:  *pip install -r requirements.txt*
3. In file auth.py enter your secret key ( recomended)
4. Type from console:  *uvicorn main:app --reload*
5. Go to yuor local browser and enter http://127.0.0.1:8000/docs#/

**How to use:**

You will see a documentation with endpoints and details about their inputs and outputs - all can be conveniently used as is. For login and logout you can use a button "Authorize" at the top right corner.

First six, that start with '/admin/' are reserved for the future, when such functionality might be added, and are for now left free to use for developers convenience - they allow retrieving information about users and links, and delete them if necessary.

At the first run database will be empty, so you can create a few instances via documentation endpoints:
First, register a user via "/register", then create a few link instances via "/users/me/links/create". 
Then, you can play around with it.
When you get a short url, you can paste it into your browser, and get the original page.

