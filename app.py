from urllib import request

from flask import Flask, render_template
from data_models import db, Author, Book
import os

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))

os.makedirs(os.path.join(basedir, 'data'), exist_ok=True)

db_path = os.path.join(basedir, 'data', 'library.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "data", "library.sqlite")}'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

#with app.app_context():
   # db.create_all()
@app.route('/')
def home():
    books = Book.query.all()
    return render_template('home.html', books=books)


@app.route('/add_author ', methods=['GET', 'POST'])
def add_author():
    message=''
    if request.method == 'POST':
        name = request.form['name']
        birth_date = request.form['birthdate']
        date_of_death = request.form['date_of_death']
        author = Author(name=name, birth_date=birth_date, date_of_death=date_of_death)
        db.session.add(author)
        db.session.commit()

        message=f"Author {name} was added successfully."

    return render_template('add_author.html', message=message)


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
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



if __name__ == '__main__':
    app.run(debug=True)
