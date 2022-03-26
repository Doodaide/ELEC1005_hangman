import random
import time
import flask
from flask_sqlalchemy import SQLAlchemy

app = flask.Flask(__name__)

# Database

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hangman.db'
db = SQLAlchemy(app)

# Model

#A list of categories that the user can choose from standard input.
#Currently, categories are: animals, countries, food, pokemon, pop_culture. 

categories = ["food","animals","pop-culture", "pokemon", "countries"] #added the rest of the categories

#I think adding a set of automated messages the would add to user interaction. I'll let someone else think of more. 
#If this is changed, we must change the selection range.

messages = ["A wise choice for a foolish soul", "Can't say I'm an expert, but I'll let you do the talking"]

selection = random.randint(0,1) 

#initial greeting message

print("Hello User")
time.sleep(1)
print("I hope you are well.")
time.sleep(1)
print("Unfortunately, our prisoner is not")
time.sleep(1)
print("It is time to test your knowledge.")
time.sleep(0.8)
print("Choose a category you are confident in")
time.sleep(0.8)
print("Confident enough that you'd gamble a life")
time.sleep(0.8)
print("Or, type random if you wish to be surprised")
time.sleep(0.8)
print("Hope you are ready :)")
time.sleep(0.8)
print()

#formatted category display to look better 
for cat in categories:
    print("-", cat.capitalize(),end='\n')
print()
category = input("Choice: ").lower().strip() #added choice mesage 

#if the category is a valid category in the list, print a selected message, then proceed
if category in categories:
    print(messages[selection])

#If the user selects random, the code will select a random category of the 5, then print a message saying 
#Looks like we'll use <category name> today, and another message before the game starts
elif category == "random":
    random_index = random.randint(0,4)
    category = categories[random_index] 
    print(f"Looks like we'll use {categories[random_index]} today")
    print(messages[selection])

#This block of code will loop the "ask user for selection" menu 
#until the user enters in a proper category
while category not in categories:
    print()
    print("Please choose a legit category:")
    print()
    for cat in categories:
        print("-", cat.capitalize(),end='\n')

    print()
    category = input("Choice: ").lower().strip()
    if category in categories:
        print(messages[selection])
    if category == "random":
        random_index = random.randint(0,4)
        category = categories[random_index] 
        print(f"Looks like we'll use {categories[random_index]} today")
        print(messages[selection])


word_file = category+".txt"

def random_pk():
    return random.randint(1e9, 1e10)

def random_word():
    words = [line.strip() for line in open(word_file) if len(line) > 10]
    return random.choice(words).upper()

class Game(db.Model):
    pk = db.Column(db.Integer, primary_key=True, default=random_pk)
    word = db.Column(db.String(50), default=random_word)
    tried = db.Column(db.String(50), default='')
    player = db.Column(db.String(50))

    def __init__(self, player):
        self.player = player

    @property
    def errors(self):
        return ''.join(set(self.tried) - set(self.word))

    @property
    def current(self):
        return ''.join([c if c in self.tried else '_' for c in self.word])

    @property
    def points(self):
        return 100 + 2*len(set(self.word)) + len(self.word) - 10*len(self.errors)

    # Play

    def try_letter(self, letter):
        if not self.finished and letter not in self.tried:
            self.tried += letter
            db.session.commit()

    # Game status

    @property
    def won(self):
        return self.current == self.word

    @property
    def lost(self):
        return len(self.errors) == 6

    @property
    def finished(self):
        return self.won or self.lost


# Controller

@app.route('/')
def home():
    games = sorted(
        [game for game in Game.query.all() if game.won],
        key=lambda game: -game.points)[:10]
    return flask.render_template('home.html', games=games)

@app.route('/play')
def new_game():
    player = flask.request.args.get('player')
    game = Game(player)
    db.session.add(game)
    db.session.commit()
    return flask.redirect(flask.url_for('play', game_id=game.pk))

@app.route('/play/<game_id>', methods=['GET', 'POST'])
def play(game_id):
    game = Game.query.get_or_404(game_id)

    if flask.request.method == 'POST':
        letter = flask.request.form['letter'].upper()
        if len(letter) == 1 and letter.isalpha():
            game.try_letter(letter)

    if flask.request.is_xhr:
        return flask.jsonify(current=game.current,
                             errors=game.errors,
                             finished=game.finished)
    else:
        return flask.render_template('play.html', game=game)

# Main

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8910, debug=False)

