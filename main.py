from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

'''
Red underlines? Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)
db = SQLAlchemy()
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///movie.db"
db.init_app(app)

API_KEY = "5a2ffe1cf2a0f78028305f7125d6cd65"
headers = {
    "accept": "application/json",
    "Authorization": "Bearer 5a2ffe1cf2a0f78028305f7125d6cd65"
}
BASE_URL_IMG = 'https://image.tmdb.org/t/p/w500/'


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String(250), nullable=False)


with app.app_context():
    db.create_all()


class RateMovieForm(FlaskForm):
    rating = StringField('Your Rating Out of 10', validators=[DataRequired()])
    review = StringField('Your Review', validators=[DataRequired()])
    done = SubmitField('Done')

class AddMovie(FlaskForm):
    title = StringField('Movie Title', validators=[DataRequired()])
    submit = SubmitField('Add Movie')


@app.route("/")
def home():
    result = db.session.execute(db.select(Movie).order_by(Movie.rating))
    all_movies = result.scalars().all()
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()

    return render_template("index.html", movies=all_movies)


@app.route("/edit", methods=["GET", "POST"])
def edit():
    id = int(request.args.get('id'))
    form = RateMovieForm()
    movie_to_update = db.get_or_404(Movie, id)
    if form.validate_on_submit():
        movie_to_update.rating = float(form.rating.data)
        movie_to_update.review = form.review.data
        db.session.commit()
        return redirect(url_for("home"))

    return render_template("edit.html", form=form)

@app.route("/delete")
def delete():
    id = request.args.get('id')
    movie_to_delete = db.get_or_404(Movie, id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for("home"))

@app.route("/add", methods=["GET", "POST"])
def add():
    form = AddMovie()
    if form.validate_on_submit():
        movie_title = form.title.data
        params = {
            "api_key": API_KEY,
            "query": movie_title
        }
        movie_data = requests.get("https://api.themoviedb.org/3/search/movie", params=params, headers=headers).json()
        return render_template("select.html", movie_data=movie_data['results'])
    return render_template("add.html", form=form)

@app.route("/find")
def find():
    id = request.args.get('id')
    data = requests.get(f"https://api.themoviedb.org/3/movie/{id}", params={"api_key": API_KEY} ,headers=headers).json()
    print(data)
    new_movie = Movie(
        title=data['original_title'],
        img_url=BASE_URL_IMG + data['poster_path'],
        year=data['release_date'][:4],
        description=data['overview']
    )
    db.session.add(new_movie)
    db.session.commit()
    return redirect(url_for('edit', id=new_movie.id))

if __name__ == '__main__':
    app.run(debug=True)
