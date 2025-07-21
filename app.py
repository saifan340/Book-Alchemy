from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
from data_models import db, Author, Book

import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'

basedir = os.path.abspath(os.path.dirname(__file__))
os.makedirs(os.path.join(basedir, 'data'), exist_ok=True)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "data", "library.sqlite")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
#with app.app_context():
   # db.create_all()





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
    message = ''
    if request.method == 'POST':
        name = request.form['name'].strip()
        birth_date_raw = request.form['birthdate'].strip()
        death_date_raw = request.form.get('date_of_death', '').strip()

        # Basic validation
        if not name:
            flash("Author name is required.")
            return redirect(url_for('add_author'))

        try:
            birth_date = datetime.strptime(birth_date_raw, '%Y-%m-%d').date()
        except ValueError:
            flash("Birth date is required and must be in YYYY-MM-DD format.")
            return redirect(url_for('add_author'))

        try:
            date_of_death = datetime.strptime(death_date_raw, '%Y-%m-%d').date() if death_date_raw else None
        except ValueError:
            flash("Date of death must be in YYYY-MM-DD format.")
            return redirect(url_for('add_author'))

        if date_of_death and date_of_death < birth_date:
            flash("Date of death cannot be before birth date.")
            return redirect(url_for('add_author'))

        # Save valid data
        author = Author(name=name, birth_date=birth_date, date_of_death=date_of_death)
        db.session.add(author)
        db.session.commit()
        flash(f"Author '{name}' added successfully.")
        return redirect(url_for('add_author'))

    return render_template('add_author.html')

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    authors = Author.query.all()
    if request.method == 'POST':
        isbn = request.form['isbn'].strip()
        title = request.form['title'].strip()
        publication_year_raw = request.form['publication_year'].strip()
        author_id_raw = request.form.get('author_id', '').strip()

        # Validate fields
        if not isbn or not title or not publication_year_raw or not author_id_raw:
            flash("All fields are required.")
            return redirect(url_for('add_book'))

        try:
            publication_year = int(publication_year_raw)
            if publication_year < 0 or publication_year > datetime.now().year:
                flash("Invalid publication year.")
                return redirect(url_for('add_book'))
        except ValueError:
            flash("Publication year must be a number.")
            return redirect(url_for('add_book'))

        try:
            author_id = int(author_id_raw)
        except ValueError:
            flash("Invalid author selection.")
            return redirect(url_for('add_book'))

        # Save book
        new_book = Book(isbn=isbn, title=title, publication_year=publication_year, author_id=author_id)
        db.session.add(new_book)
        db.session.commit()
        flash(f"Book '{title}' added successfully.")
        return redirect(url_for('add_book'))

    return render_template('add_book.html', authors=authors)


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
    app.run(host="0.0.0.0",port=5002,debug=True)