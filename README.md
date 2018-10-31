## Basic Flask and SQLAlchemy app. Book reading wishlist.

### Setup

In terminal/command prompt, root directory of the project.

Set up virtual environment, Mac

```
virtualenv -p python3 venv
source venv/bin/activate
```

Set up virtual environment, PC (assuming lab PC with only Python 3 installed)

```
virtualenv venv
venv/bin/activate
```

### Install requirements

```
pip install -r requirements.txt
```

Configure Flask environment variables, Mac

```
export FLASK_APP=book_wishlist.py
export FLASK_DEBUG=1
export DATABASE_URL=sqlite:///wishlist.db
```

Configure Flask environment variables, PC

```
set FLASK_APP=book_wishlist.py
set FLASK_DEBUG=1
set DATABASE_URL=sqlite:///wishlist.db
```

Run app

```
flask run
```

App should be at http://127.0.0.1:5000


Run tests by typing

```
python -m unittest tests.test_book_wishlist
```
or
```
python -m unittest tests/test_book_wishlist.py
```

-------------

## Deployment to Heroku

Create a Heroku account and install Heroku command line tools. 

Add latest versions of psycopg2 and gunicorn to requirements.txt

Create a **Procfile** with this line in it

```
web: gunicorn book_wishlist:app
```

Ensure you've got all of your latest changes committed and create a Heroku app with
```
heroku apps:create
```

Provision Postgres add on

```
heroku addons:create heroku-postgresql
```

Get DB connection URL with

```
heroku config
```

(Suggested but optional) Copy the URL and set as local env variable `DATABASE_URL` for local testing but with your Postgres database

Verify things are working with

```
heroku local web
```

All good?

```
git push heroku master
```

```
heroku open
```
