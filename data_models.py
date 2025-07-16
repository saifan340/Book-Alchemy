from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
class Author (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.String(50), nullable=False)
    date_of_death= db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<Author {self.name}>'

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True,  autoincrement=True)
    isbn= db.Column(db.String(13), nullable=False, unique=True)
    title = db.Column(db.String(200), nullable=False)
    publication_year = db.Column(db.Integer, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=False)
    author = db.relationship('Author', backref=db.backref('books', lazy=True))
    def __repr__(self):
        """
        Official representation of the Book object for debugging.
        """
        return f'<Book {self.title!r}>'

    def __str__(self):
        """
        String representation of the Book object.
        """
        return self.title





