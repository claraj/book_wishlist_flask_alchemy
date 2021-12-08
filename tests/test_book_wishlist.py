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
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///testing_db.db'
        app.config['TESTING'] = True
        self.app = app.test_client()
        book_wishlist.init_db()


    def tearDown(self):
        book_wishlist.db.drop_all()
        book_wishlist.db.session.close()


    # Helper method to add example data
    def add_example_books(self):

        test_book1 = Book('Dr Seuss', 'The Lorax', True)
        test_book2 = Book('Alice Walker', 'The Color Purple', True)
        test_book3 = Book('George Orwell', '1984', False)
        test_book4 = Book('Aldous Huxley', 'Brave New World', False)

        self.test_books = [ test_book1, test_book2, test_book3, test_book4 ]

        book_wishlist.db.session.add_all(self.test_books)
        book_wishlist.db.session.commit()


    # Test empty db
    def test_empty_database(self):

        response = self.app.get('/booklist/UNREAD')
        self.assertIn(b'No books', response.data)

        response = self.app.get('/booklist/ALL')
        self.assertIn(b'No books', response.data)

        response = self.app.get('/', follow_redirects=True)
        self.assertIn(b'No books', response.data)

        response = self.app.get('/booklist/READ')
        self.assertIn(b'No books', response.data)


    def test_add_new_book(self):

        # Add unread book. Should be added to db and redirected to info page on that book.
        response = self.app.post('/add', data=dict(title='1984',author='George Orwell'), follow_redirects=True)
        self.assertIn(b'1984', response.data)
        self.assertIn(b'George Orwell', response.data)
        self.assertIn(b'Read: no', response.data)

        # In db?
        self.assertEqual(len(Book.query.all()), 1)

        # Add read book
        response = self.app.post('/add', data=dict(title='Brave New World',author='Aldous Huxley', read=True), follow_redirects=True)
        self.assertIn(b'Brave New World', response.data)
        self.assertIn(b'Aldous Huxley', response.data)
        self.assertIn(b'Read: yes', response.data)

        # Second book in db?
        self.assertEqual(len(Book.query.all()), 2)

        book_from_db = Book.query.filter_by(title='Brave New World').filter_by(author='Aldous Huxley').filter_by(read=True).one_or_none()
        self.assertIsNotNone(book_from_db)

        book_from_db = Book.query.filter_by(title='1984').filter_by(author='George Orwell').filter_by(read=False).one_or_none()
        self.assertIsNotNone(book_from_db)


    def test_book_detail_view(self):

        test_book = Book('The Lorax', 'Dr Seuss', True)
        book_wishlist.db.session.add(test_book)
        book_wishlist.db.session.commit()

        response = self.app.get('/book/1')
        self.assertIn(b'The Lorax', response.data)
        self.assertIn(b'Dr Seuss', response.data)
        self.assertIn(b'id: 1', response.data)
        self.assertIn(b'Read: yes', response.data)


    def test_book_detail_view_404_if_book_does_not_exist(self):
        # Get non-existent book. Expect 404
        response = self.app.get('/book/2')
        self.assertEqual(404, response.status_code)


    def test_view_all_books(self):

        self.add_example_books()

        response = self.app.get('/booklist/ALL')

        self.assertIn(b'Alice Walker', response.data)
        self.assertIn(b'George Orwell', response.data)
        self.assertIn(b'Dr Seuss', response.data)
        self.assertIn(b'Aldous Huxley', response.data)


    def test_view_all_unread_books(self):

        self.add_example_books()

        response = self.app.get('/booklist/UNREAD')

        self.assertIn(b'Aldous Huxley', response.data)
        self.assertIn(b'George Orwell', response.data)


    def test_view_all_read_books(self):

        self.add_example_books()

        response = self.app.get('/booklist/READ')

        self.assertIn(b'Alice Walker', response.data)
        self.assertIn(b'Dr Seuss', response.data)


    def test_mark_book_as_read(self):

        # Create an unread book. Change it to read=True
        test_book = Book('Dr Seuss', 'The Lorax', False)
        book_wishlist.db.session.add(test_book)
        book_wishlist.db.session.commit()

        response = self.app.post('/book/read', data=dict(book_id=test_book.book_id, read=True), follow_redirects=True)

        book_from_db = Book.query.filter_by(title='The Lorax').filter_by(author='Dr Seuss').filter_by(read=True).one_or_none()
        self.assertIsNotNone(book_from_db)
        self.assertIn(b'Read: yes', response.data)


    def test_mark_book_as_unread(self):

        # Create a read book. Change it to read=False
        test_book = Book('Charles Dickens', 'Great Expectations', True)
        book_wishlist.db.session.add(test_book)
        book_wishlist.db.session.commit()

        response = self.app.post('/book/read', data=dict(book_id=test_book.book_id, read=False), follow_redirects=True)
        book_from_db_2 = Book.query.filter_by(title='Great Expectations').filter_by(author='Charles Dickens').filter_by(read=False).one_or_none()

        self.assertIsNotNone(book_from_db_2)
        self.assertIn(b'Read: no', response.data)


    def test_change_read_nonexistent_books(self):

        # Try to change to upread, a book that does not exist
        response = self.app.post('/book/read', data=dict(book_id=123, read=False), follow_redirects=True)
        self.assertEquals(404, response.status_code)
        # Try to change to read, a book that does not exist
        response = self.app.post('/book/read', data=dict(book_id=123, read=True), follow_redirects=True)
        self.assertEquals(404, response.status_code)
        

    # Test delete book by id
    def test_delete_by_id(self):

        test_book = Book('Dr Seuss', 'The Lorax', False)
        book_wishlist.db.session.add(test_book)
        book_wishlist.db.session.commit()

        response = self.app.delete('/book/' + str(test_book.book_id))
        self.assertEquals(200, response.status_code)
        self.assertEqual(b'deleted', response.data)

        # Make sure not in db
        book_from_db = Book.query.filter_by(title='The Lorax').filter_by(author='Dr Seuss').filter_by(read=True).one_or_none()
        self.assertIsNone(book_from_db)

        # Delete book that doesn't exist. Should still return 200 and 'not_found'

        response = self.app.delete('/book/12')
        self.assertEqual(200, response.status_code)
        self.assertEqual(b'not_found', response.data)


if __name__ == '__main__':
    unittest.main()
