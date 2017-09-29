from book_wishlist import db

class Book(db.Model):

    ''' Represents one book in a user's list of books '''

    __tablename__ = 'books'

    book_id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String, nullable=False)
    title = db.Column(db.String, nullable=False)
    read = db.Column(db.Boolean, default=False)


    def __init__(self, author, title, read=False):
        self.author=author
        self.title=title
        self.read=read


    def __repr__(self):
        read_str = 'no'
        if self.read:
            read_str = 'yes'

        id_str = self.book_id
        if self.book_id == -1:
            id_str = '(no id)'

        template = 'id: {} Title: {} Author: {} Read: {}  Bool {}'
        return template.format(id_str, self.title, self.author, read_str, self.read)
