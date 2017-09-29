import os
#import book_wishlist
#from book_wishlist import app
import book_wishlist
from book_wishlist import app
import unittest
import tempfile
from models import Book


class TestWishList(unittest.TestCase):

    def setUp(self):
        #self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///testing_db.db'
        app.config['TESTING'] = True
        self.app = app.test_client()
        # with app.app_context():
        book_wishlist.init_db()


    def tearDown(self):
        #os.close(self.db_fd)
        #os.unlink(app.config['DATABASE'])
        book_wishlist.db.drop_all()
        book_wishlist.db.session.close()


    # Test empty db
    def test_empty_database(self):

        rv = self.app.get('/booklist/UNREAD')
        assert b'No books' in rv.data

        rv = self.app.get('/booklist/ALL')
        assert b'No books' in rv.data

        rv = self.app.get('/', follow_redirects=True)
        assert b'No books' in rv.data

        rv = self.app.get('/booklist/READ')
        assert b'No books' in rv.data


    # Test add read book
    def test_add_new_book(self):

        # Add unread book. Should be added to db and redirected to info page on that book.
        rv = self.app.post('/add', data=dict(title='1984',author='George Orwell'), follow_redirects=True)
        assert b'1984' in rv.data
        assert b'George Orwell' in rv.data
        assert b'Read: no' in rv.data

        # In db?
        assert len(Book.query.all()) == 1

        # Add read book
        rv = self.app.post('/add', data=dict(title='Brave New World',author='Aldous Huxley', read=True), follow_redirects=True)
        assert b'Brave New World' in rv.data
        assert b'Aldous Huxley' in rv.data
        assert b'Read: yes' in rv.data

        # In db?
        assert len(Book.query.all()) == 2

        book_from_db = Book.query.filter_by(title='Brave New World').filter_by(author='Aldous Huxley').filter_by(read=True).one_or_none()
        assert book_from_db is not None

        book_from_db = Book.query.filter_by(title='1984').filter_by(author='George Orwell').filter_by(read=False).one_or_none()
        assert book_from_db is not None


    # test book detail view
    def test_book_detail_view(self):

        test_book = Book('The Lorax', 'Dr Seuss', True)
        book_wishlist.db.session.add(test_book)
        book_wishlist.db.session.commit()

        rv = self.app.get('/book/1')
        assert b'The Lorax' in rv.data
        assert b'Dr Seuss' in rv.data
        assert b'id: 1' in rv.data
        assert b'Read: yes' in rv.data


        # Get non-existent book. Expect 404
        rv = self.app.get('/book/2')
        assert rv.status_code == 404



    # Test view all books
    def test_view_all_books(self):

        self.add_example_books()

        rv = self.app.get('/booklist/ALL')

        assert b'Alice Walker' in rv.data
        assert b'George Orwell' in rv.data
        assert b'Dr Seuss' in rv.data
        assert b'Aldous Huxley' in rv.data


    # Test view books in wishlist
    def test_view_all_unread_books(self):

        self.add_example_books()

        rv = self.app.get('/booklist/UNREAD')

        assert b'Aldous Huxley' in rv.data
        assert b'George Orwell' in rv.data


    # Test view books that have been read
    def test_view_all_read_books(self):

        self.add_example_books()

        rv = self.app.get('/booklist/READ')

        assert b'Alice Walker' in rv.data
        assert b'Dr Seuss' in rv.data


    # Test mark book as read
    def test_mark_book_as_read(self):

        # Create an unread book. Change it to read=True
        test_book = Book('Dr Seuss', 'The Lorax', False)
        book_wishlist.db.session.add(test_book)
        book_wishlist.db.session.commit()

        rv = self.app.post('/book/read', data=dict(book_id=test_book.book_id, read=True), follow_redirects=True)

        # assert test_book.read == True  # object detatched (?)
        book_from_db = Book.query.filter_by(title='The Lorax').filter_by(author='Dr Seuss').filter_by(read=True).one_or_none()
        assert book_from_db is not None
        assert b'Read: yes' in rv.data


    def test_mark_book_as_unread(self):

        # Create a read book. Change it to read=False
        test_book = Book('Charles Dickens', 'Great Expectations', True)
        book_wishlist.db.session.add(test_book)
        book_wishlist.db.session.commit()

        rv = self.app.post('/book/read', data=dict(book_id=test_book.book_id, read=False), follow_redirects=True)
        book_from_db_2 = Book.query.filter_by(title='Great Expectations').filter_by(author='Charles Dickens').filter_by(read=False).one_or_none()

        assert book_from_db_2 is not None
        assert b'Read: no' in rv.data


    def test_change_read_nonexistent_books(self):

        # Try to change read value of a book that does not exist
        rv = self.app.post('/book/read', data=dict(book_id=123, read=False), follow_redirects=True)
        assert rv.status_code == 500
        # Try to change read value of a book that does not exist
        rv = self.app.post('/book/read', data=dict(book_id=123, read=True), follow_redirects=True)
        assert rv.status_code == 500


    # Test delete book by id
    def test_delete_by_id(self):

        test_book = Book('Dr Seuss', 'The Lorax', False)
        book_wishlist.db.session.add(test_book)
        book_wishlist.db.session.commit()

        rv = self.app.delete('/book/' + str(test_book.book_id))
        assert rv.status_code == 200
        assert rv.data == b'deleted'

        # Make sure not in db
        book_from_db = Book.query.filter_by(title='The Lorax').filter_by(author='Dr Seuss').filter_by(read=True).one_or_none()
        assert book_from_db is None

        # Delete book that doesn't exist. Should still return 200 and 'not_found'

        rv = self.app.delete('/book/12')
        assert rv.status_code == 200
        assert rv.data == b'not_found'


    def add_example_books(self):

        test_book1 = Book('Dr Seuss', 'The Lorax', True)
        test_book2 = Book('Alice Walker', 'The Color Purple', True)
        test_book3 = Book('George Orwell', '1984', False)
        test_book4 = Book('Aldous Huxley', 'Brave New World', False)

        self.test_books = [ test_book1, test_book2, test_book3, test_book4 ]

        book_wishlist.db.session.add_all(self.test_books)
        book_wishlist.db.session.commit()




if __name__ == '__main__':
    unittest.main()
