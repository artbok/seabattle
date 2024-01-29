import os
import time
from datetime import datetime
from flask import Flask, render_template, request, url_for, redirect, session, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "456jk456gj4kdfugi734fuhu83ceji"

db = SQLAlchemy(app)

connectedUsers = dict()

#username: Admin
#password: 12345

def current_milli_time():
    return round(time.time() * 1000)

class User(db.Model):
    username = db.Column(db.String, primary_key=True)
    password = db.Column(db.String)

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return f'<User {self.username} {self.password} {self.is_admin}>'
    

class Field(db.Model):
    name = db.Column(db.String, primary_key=True)
    n = db.Column(db.Integer)
    field = db.Column(db.String)
    ships = db.Column(db.String)
    def __init__(self, name, n, field, ships):
        self.name = name
        self.n = n
        self.field = field
        self.ships = ships


def addField():
    global editableField
    field = getField(editableField.name)
    if not field:
        field = Field(editableField.name, editableField.n, str(editableField.field), str(editableField.ships))
        db.session.add(field)
    else:
        field.field = str(editableField.field)
        field.ships = str(editableField.ships)
    db.session.commit()
    editableField = None


def getField(fieldname) -> Field:
    return Field.query.filter(Field.name == fieldname).first()


class EditField:
    name = ""
    n = 0
    field = []
    ships = set()
    changeId: int = 0
    def __init__(self, name, n, field = None, ships = None):
        self.name = name
        self.n = n
        if not field:
            for _ in range(n + 1):
                self.field.append([0] * (n + 1))    
        else:
            self.field = field
        if ships:
            self.ships = ships
    
    def __repr__(self) -> str:
        visualisation = ""
        for i in self.field:
            visualisation += str(i) + '\n'
        return visualisation
    
    def placeShip(self, x, y) -> bool:
        if self.field[x][y]:
            self.field[x][y] = 0
            self.ships.remove((x, y))
            self.changeId = current_milli_time()
            return True
        else:
            can_place = ((self.field[x - 1][y-1] == 0) and (self.field[x - 1][y+1] == 0) 
                    and (self.field[x + 1][y-1] == 0) and (self.field[x + 1][y+1] == 0)
                    and (self.field[x][y-1] == 0) and (self.field[x + 1][y] == 0)
                    and (self.field[x][y+1] == 0) and (self.field[x - 1][y] == 0))
            if can_place:
                self.field[x][y] = 1
                self.ships.add(str((x, y)))
                self.changeId = current_milli_time()
                return True
        return False


editableField: EditField = None

class Player:
    shots = 2
    prizes = []
    def __init__(self, username):
        self.username = username


class GameField:
    changeId = 0
    players: list[Player] = []
    prizes = dict()
    i = 0
    titles = []
    def __init__(self, field: Field):
        self.name = field.name
        self.n = field.n
        self.field = eval(field.field)
        self.ships = eval(field.ships)
    def addTitle(self, title):
        if len(self.titles) <= 1:
            self.titles.append(title)
        else:
            self.titles[0], self.titles[1] = self.titles[1], self.titles[0]
            self.titles[1] = title
    def getTitle(self):
        return "\n".join(self.titles)
    
    def fire(self, x, y):
        value = self.field[x][y]
        self.field[x][y] = -1
        i = abs(i - 1) if len(self.players) >= 2 and self.players[abs(i - 1)].shots > 0 else 0
        if value == 1:
            return self.prizes[f"({x}, {y})"]
        else:
            if value == -1:
                return None
            return False
        

game = None
def getUser(username) -> User:
    return User.query.filter(User.username == username).first()


def addUser(username: str, password):
    user = User(username, password)
    db.session.add(user)
    db.session.commit()


def isAuthorized() -> bool:
    if "username" in session and "password" in session:
        user = getUser(session["username"])
        if user and session["password"] == user.password:
            return True
    return False

def adminPage(page):
    if "username" in session and "password" in session:
        user = getUser(session["username"])
        if user and session["password"] == user.password:
            if user.username == "admin":
                return page
            return render_template("access-denied.html")
    return redirect(url_for('login'))


@app.route('/waiting', methods = ["GET"])
def waitingScreen():
    if not isAuthorized(): return redirect(url_for('login'))
    return render_template("waiting-screen.html", username = session["username"])

@app.route('/waiting', methods = ["POST"])
def checkOnline():
    connectedUsers[session["username"]] = current_milli_time()
    print(f'{session["username"]} is online!')
    if game and game.players != 0:
        for player in game.players:
            if session["username"] == player.username:
                return "GAME"
    return "Ok!"

@app.route('/')
def main():
    db.create_all()
    if not isAuthorized(): return redirect(url_for('login'))
    if session["username"] != "admin":
        return redirect(url_for("waitingScreen"))
    return redirect(url_for("fields"))
    

@app.route('/registration', methods = ["GET"])
def registration():
    if isAuthorized(): return redirect(url_for('main'))
    return render_template('registration.html')


@app.route('/registration', methods = ["POST"])
def getRegistrationData():
    username = request.form['username'].lower()
    password = request.form["password"].lower()
    if getUser(username):
        return "Account with that username already exists!"
    addUser(username, password)
    session["username"] = username
    session["password"] = password
    session.permanent = True
    return redirect(url_for("waitingScreen"))


@app.route('/login', methods = ['GET'])
def login():
    if isAuthorized():
        return redirect(url_for('main'))
    return render_template("authorization.html")


@app.route('/login', methods = ['POST'])
def getLoginData():
    username = request.form['username'].lower()
    password = request.form["password"].lower()
    user = getUser(username)
    if not user or password != user.password:
        return render_template('auth_error.html')
    session["username"] = username
    session["password"] = password
    session.permanent = True
    return redirect(url_for('waiting-screen'))


@app.route('/fields', methods=['GET'])
def fields():
    fields = []
    for field in list(Field.query):
        fields.append(field.name)
    return adminPage(render_template('view-fields.html', fields = fields))


@app.route('/fields', methods=['POST'])
def getFieldButtonClick():
    global editableField, game
    if "play" in request.form:
        field = getField(request.form["play"])
        game = GameField(field)
        return redirect(url_for("setupPrizes"))
    elif "edit" in request.form:
        field = getField(request.form["edit"])
        editableField = EditField(field.name, field.n, eval(field.field), eval(field.ships))
        return redirect(url_for("fieldEditing"))
    elif "delete" in request.form:
        Field.query.filter(Field.name == request.form["delete"]).delete()
        db.session.commit()
        getField(request.form["delete"])
        db.session.commit()
        return adminPage(redirect(url_for('fields')))
    else:
        return adminPage(redirect(url_for("creatingField")))

@app.route('/creating-field', methods=['GET'])
def creatingField():
    return adminPage(render_template("creating-field.html", suggestedName = f'Игра-{datetime.now().strftime("%d/%m/%H:%M:%S")}'))


@app.route('/creating-field', methods=["POST"])
def getFieldSettings():
    global editableField
    fieldsize = int(request.form['fieldsize'])
    fieldname = request.form["fieldname"]
    editableField = EditField(fieldname, fieldsize+1)
    return redirect(url_for('fieldEditing'))


@app.route('/field-editing', methods=['GET'])
def fieldEditing():
    if editableField == None: 
        return adminPage(redirect(url_for("fields")))
    return adminPage(render_template('fieldediting.html', field = editableField.field, len = editableField.n))


@app.route('/field-editing', methods=['POST'])
def saveField():
    addField()
    return render_template("field-saved.html")


@app.route('/field-cell-update', methods = ['POST'])
def cellUpdate():
    data = request.json
    x = data['x']
    y = data['y']
    if editableField.placeShip(x, y):
        return ""
    else:
        return "error"
    

@app.route('/wait-field-update', methods = ['POST'])
def waitFieldUpdate():
    if not game:
        return "RELOAD"
    changeId = int(session["changeId"] if "changeId" in session else 0)
    if game.changeId > changeId:
        session["changeId"] = editableField.changeId
        return "UPDATE: changeId = " + str(changeId)
    return "WAIT"
    

@app.route('/setup-prizes', methods=['GET'])
def setupPrizes():
    if not game:
        return adminPage(redirect(url_for("fields")))
    return adminPage(render_template("setup-prizes.html", poses = game.ships))


@app.route('/setup-prizes', methods=['POST'])
def getPrizes():
    rewards = dict()
    for pos in game.ships:
        name = "prizeFor" + str(pos)
        if name in request.form:
            rewards[pos] = request.form[name]
    game.prizes = rewards
    return redirect(url_for('addPlayers'))


@app.route('/add-players', methods=['GET'])
def addPlayers():
    if not game:
        return adminPage(redirect(url_for("fields")))
    now = current_milli_time()
    players = []
    for player in connectedUsers.keys():
        if now - connectedUsers[player] < 17000:
            players.append(player)
    return adminPage(render_template("add-players.html", players = players))


@app.route('/add-players', methods=['POST'])
def startGame():
    player1 = request.form["player1"]
    player2 = request.form["player2"]
    game.players.append(Player(request.form["player1"]))
    if player1 != player2:
        game.players.append(Player(request.form["player2"]))
    return redirect(url_for('gameScreen'))
    

@app.route('/game', methods = ['GET'])
def gameScreen():
    if not isAuthorized(): 
        return redirect(url_for('login'))
    for player in game.players:
        if session["username"] == player.username:
            return render_template('gameScreen.html', field = game.field, len = game.n, action = game.getTitle())
    return 'none'


@app.route('/fire', methods=['POST'])
def shot():
    data = request.json
    x = data['x']
    y = data['y']
    player = game.players[game.i]
    if player.username == session["username"]:
        if player.shots <= 0:
            return "NOAMMO"
        prize = game.fire(x, y)
        if prize == None:
            return "Error"
        elif prize == False:
            player.shots -= 1
            return "MISS"
        else:
            player.shots -= 1
            player.prizes.append(prize)
            return 'HIT'
    else:
        return 'notYourMove'
    
if __name__ == '__main__':
    app.run()