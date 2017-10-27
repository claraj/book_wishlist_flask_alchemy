## Basic Flask and SQLAlchemy app. Book reading wishlist.

### Setup

In terminal/command prompt, root directoty of the project.

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

App should be at 127.0.0.1:5000


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

Add psycopg2 and gunicorn to requirements.txt

Create a **Procfile** with this line in it

```
web: gunicorn app:book_wishlist
```

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

Copy the URL and set as local env var if desired
