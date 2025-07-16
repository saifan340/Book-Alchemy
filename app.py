from flask import Flask, render_template, request, redirect, url_for, flash

from data_models import db, Author, Book

import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'

basedir = os.path.abspath(os.path.dirname(__file__))
os.makedirs(os.path.join(basedir, 'data'), exist_ok=True)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "data", "library.sqlite")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    """display home page"""
    search_query = request.args.get('q', '')
    sort_by = request.args.get('sort_by', '')

    query = Book.query.join(Author)

    if search_query:
        query = query.filter(Book.title.ilike(f'%{search_query}%'))

    if sort_by == 'title':
        query = query.order_by(Book.title)
    elif sort_by == 'author':
        query = query.order_by(Author.name)

    books = query.all()

    return render_template('home.html', books=books, sort_by=sort_by)


@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    """Add a new author to the database."""
    message = ''
    if request.method == 'POST':
        name = request.form['name']
        birth_date = request.form['birthdate']
        date_of_death = request.form['date_of_death']
        author = Author(name=name, birth_date=birth_date, date_of_death=date_of_death)
        db.session.add(author)
        db.session.commit()
        message = f"Author {name} was added successfully."
    return render_template('add_author.html', message=message)

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    """adds a book to the database"""
    message = ''
    authors = Author.query.all()
    if request.method == 'POST':
        isbn = request.form['isbn']
        title = request.form['title']
        publication_year = int(request.form['publication_year'])
        author_id = int(request.form['author_id'])

        new_book = Book(isbn=isbn, title=title, publication_year=publication_year, author_id=author_id)
        db.session.add(new_book)
        db.session.commit()
        message = f"Book '{title}' was added successfully."
    return render_template('add_book.html', authors=authors, message=message)

@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    """Delete book from the database."""
    book = Book.query.get_or_404(book_id)
    author = book.author

    db.session.delete(book)
    db.session.commit()

    remaining_books = Book.query.filter_by(author_id=author.id).count()
    if remaining_books == 0:
        db.session.delete(author)
        db.session.commit()
        flash(f"Book '{book.title}' and author '{author.name}' were deleted.")
    else:
        flash(f"Book '{book.title}' was deleted.")

    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
