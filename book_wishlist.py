from flask import Flask
from flask import url_for, render_template, request, redirect, flash, abort
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)


DEBUG = True     # Turns logging features on for code. Separate to the in-browser debugger and code-relaucher.
SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']   #Set this environment variable e.g. 'sqlite:///wishlist.db' or your Heroku Postgres DB or whatever. In a SQLite link, three slashes means /// relative path to this app.    Four slashes //// absolute path to somewhere on file system
SECRET_KEY = 'super random super secret value'  # Replace with an actual secret key read in from private data store e.g. env variable or other file ignored by git


app.config.from_object(__name__)

db = SQLAlchemy(app)

def init_db():
    db.create_all()

from models import *

init_db()



"""Application home page. Redirects to list of unread books."""
@app.route('/')
def home_page():
    return redirect(url_for('show_books', read='UNREAD'))



@app.route('/add', methods=['POST', 'GET'])
def add_book():

    if request.method == 'POST':
        # A POST request to this URL, to create a book

        # Validate that both of the necessary parameters are provided.
        if 'author' not in request.form or 'title' not in request.form:
            app.logger.error('Attempt to create book without both author and title')
            abort(500)

        author = request.form['author']
        title = request.form['title']

        if not author or not title:
            app.logger.error('Attempt to create book without both author and title')
            flash('Please enter both title and author')
            return redirect(url_for('add_book'))

        # Checkboxes don't include any data in the post request if not checked.
        # If there's no data for the 'read' parameter, assume checkbox was not checked.
        if 'read' in request.form:
            read = request.form['read']
        else:
            read = False

        book = Book(author, title, read)
        db.session.add(book)
        db.session.commit()

        return redirect(url_for('book_info', book_id=book.book_id))

    else:
        #A GET request. Show the add book form
        return render_template('add_book.html')



@app.route('/book/<int:book_id>')
def book_info(book_id):
    
    """Get book info for an ID, or 404 if book id not found"""
    
    book = Book.query.get_or_404(book_id)           # Raise 404 if book not found.
    return render_template('book.html', book=book)



@app.route('/book/read', methods=['POST'])
def book_read():

    """Change the read value for a book. The id and read = True or False in the POST parameters """
    
    #Was book read or not? this could be used to make read book as unread.
    read_str = request.form['read']  # Form data is strings
    read = read_str == 'True'
    book_id = request.form['book_id']

    book = Book.query.get(book_id)   # get() function for fetching by primary key.

    if book:
        book.read = read
        #db.session.add(book)
        db.session.commit()
        flash('Book updated.')

    else :
        app.logger.warning('Attempt to update book id %s but book was not found in DB' % book_id)
        abort(404)   # Invalid request. Return 404 client error code.

    return redirect(url_for('book_info', book_id=book_id))



@app.route('/booklist/<read>')
def show_books(read):

    """Fetch all books, or fetch books based on read or unread."""
    
    if read == 'read':
        title = 'Books you\'ve read'
        booklist = Book.query.filter_by(read=True).all()

    elif read == 'unread':
        title = 'Books to read'
        booklist = Book.query.filter_by(read=False).all()

    else:
        title = 'All books'
        booklist = Book.query.all()

    return render_template('booklist.html', title=title, booklist=booklist)



@app.route('/book/<int:book_id>', methods=['DELETE'])

def delete_book(book_id):
    
    """ Delete a book by ID """
    
    book = Book.query.get(book_id)
    if book:
        db.session.delete(book)
        db.session.commit()
        return 'deleted', 200  # Text response and 200 status code = OK.

    else :
        app.logger.warning('Attempt to delete book id %s but book was not found in db. ' % book_id)
        return 'not_found', 200  # Text response. There was nothing to delete, so the thing the user wants gone is gone. So, not an error. 200 succes code




@app.errorhandler(404)
def page_not_found(error):
    return render_template('not_found.html'), 404
