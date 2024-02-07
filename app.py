import os
import time
from datetime import datetime
from flask import Flask, render_template, request, url_for, redirect, session, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from asyncio import sleep

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


class Prize(db.Model):
    name = db.Column(db.String, primary_key=True)
    owner = db.Column(db.String)
    receiewingDate = db.Column(db.DateTime, default = datetime.now())
    def __init__(self, name, owner):
        self.name = name
        self.owner = owner
        

def addPrize(name, username):
    prize = Prize(name, username)
    db.session.add(prize)
    db.session.commit()


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
    field = None
    ships = None
    changeId = 0
    def __init__(self, name, n, field = list(), ships = set()): 
        self.name = name
        self.n = n
        self.field: list[list] = field
        self.ships = ships
        self.changeId = 0
        alphabet = ['', 'А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ж', 'З', 'И', 'К', 'Л', 'М', 'Н', 'О', 'П', 'Р', 'С', 'Т', 'У', 'Ф', 'Х', 'Ц', 'Ч', 'Ш', 'Э', 'Ю', 'Я'] 
        if not field: 
            self.field.append(alphabet[:(n+1)])
            for i in range(1, n + 1): 
                self.field.append([0] * (n+1))
                self.field[i][0] = str(i)
        else:
            self.field = field 
        if ships: 
            self.ships = ships 

    def placeShip(self, x, y) -> bool: 
        if self.field[x][y]: 
            self.field[x][y] = 0 
            self.ships.remove(getPos(x, y)) 
            self.changeId = current_milli_time() 
            return True 
        else: 
            can_place = ((x == self.n or (self.field[x + 1][y-1] != 1 and self.field[x + 1][y] != 1)) 
                         and (y == self.n or (self.field[x - 1][y+1] != 1 and self.field[x][y+1] != 1))  
                         and ((y == self.n or x == self.n) or (self.field[x + 1][y+1] != 1))  
                         and (self.field[x][y-1] != 1 and self.field[x - 1][y] != 1 and self.field[x - 1][y-1] != 1)) 
            if can_place: 
                self.field[x][y] = 1 
                self.ships.add(getPos(x, y)) 
                self.changeId = current_milli_time() 
                return True 
        return False


editableField: EditField = None

class Player:
    shots = 2
    prizes = []
    def __init__(self, username):
        self.username = username
    
def getPos(x, y):
    alphabet = {1: "А", 2: "Б", 3: "В", 4: "Г", 5: "Д", 6: "Е", 7: "Ж", 8: "З", 9: "И", 10: "К", 11: "Л", 12: "М", 13: "Н", 14: "О", 15: "П", 16: "Р", 17: "С", 18: "Т", 19: "У", 20: "Ф", 21: "Х", 22: "Ц", 23: "Ч", 24: "Ш", 25: "Э", 26: "Ю", 27: "Я"}
    return alphabet[y] + str(x)

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
    
    def getTitle(self):
        return " | ".join(self.titles)
    
    def fire(self, x, y):
        value = self.field[x][y]
        self.field[x][y] = -1
        pos = getPos(x, y)
        
        self.changeId = current_milli_time()
        if value == 1:
            prize = self.prizes[pos]
            del self.prizes[pos]
            self.field[x][y] = -10
            self.titles.append(f"На {pos} был корабль! Получен приз:\n{prize}")
            self.players[self.i].prizes.append(prize)
            self.i = abs(self.i - 1) if len(self.players) >= 2 and self.players[abs(self.i - 1)].shots > 0 else 0
            return prize
        self.i = abs(self.i - 1) if len(self.players) >= 2 and self.players[abs(self.i - 1)].shots > 0 else 0
        self.titles.append(f"На {pos} ничего не было! Промах...")
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
        return render_template("registration-error.html")
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
    del editableField
    editableField = EditField(fieldname, fieldsize, [], set())
    return redirect(url_for('fieldEditing'))


@app.route('/field-editing', methods=['GET'])
def fieldEditing():
    if editableField == None: 
        return adminPage(redirect(url_for("fields")))
    return adminPage(render_template('fieldediting.html', field = editableField.field, len = editableField.n + 1))


@app.route('/field-editing', methods=['POST'])
def saveField():
    if len(editableField.ships) != 0:
        addField()
        return render_template("field-saved.html")
    return render_template("field-editing-error.html")


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
        session["changeId"] = game.changeId
        return "UPDATE: changeId = " + str(changeId)
    return "WAIT"
    

@app.route('/setup-prizes', methods=['GET'])
def setupPrizes():
    if not game:
        return adminPage(redirect(url_for("fields")))
    return adminPage(render_template("setup-prizes.html", poses = game.ships))


@app.route('/setup-prizes', methods=['POST'])
def getPrizes():
    if not game:
        return redirect("fields")
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
    global game
    if not isAuthorized(): 
        return redirect(url_for('login'))
    if session["username"] == 'admin':
        if not game:
            return redirect(url_for('fields'))
        players = [(player.username, player.shots) for player in game.players]
        return render_template('admin-game.html', field = game.field, len = game.n + 1, move = f"{game.players[game.i].username} выбирает куда сбросить ядерку", players = players, remain=len(game.ships), actions=game.titles)
    else:
        if game:
            s = True
            for player in game.players:
                if player.shots != 0:
                    s = False
            if (len(game.prizes) == 0 or s) and game.changeId:
                game.changeId = current_milli_time()
                prizes = []
                for player in game.players:
                    if player.username == session["username"]:
                        prizes = player.prizes
                        game.players.remove(player)
                        break
                if len(game.players) == 0:
                    game = None
                return render_template('game-over.html', prizes=prizes, len = len(prizes))

            for player in game.players:
                if session["username"] == player.username:
                    move = "ВАШ ХОД! СТРЕЛЯЙТЕ!" if game.players[game.i] == player else "ДОЖДИСЬ СВОЕГО ХОДА!"
                    return render_template('player-game.html', field = game.field, len = game.n + 1, move = move, remain = len(game.ships), shots = player.shots, actions = game.titles)
        return redirect(url_for('waitingScreen'))


@app.route('/fire', methods=['POST'])
def shot():
    data = request.json
    x = data['x']
    y = data['y']
    player = game.players[game.i]
    if player.username == session["username"]:
        if player.shots <= 0:
            return "noShots"
        prize = game.fire(x, y)
        if prize == False:
            player.shots -= 1
            return "miss"
        else:
            player.shots -= 1

            return 'hit'
    else:
        return 'notYourMove'
    
@app.route('/addShot', methods=['POST'])
def addShot():
    data = request.json
    username = data['username']
    for player in game.players:
        if player.username == username:
            player.shots += 1
    game.changeId = current_milli_time()
    return 'OK'

if __name__ == '__main__':
    app.run()