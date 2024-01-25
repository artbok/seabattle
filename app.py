import os
import time
from flask import Flask, render_template, request, url_for, redirect, session, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "456jk456gj4kdfugi734fuhu83ceji"

db = SQLAlchemy(app)

editableField = None

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
    def __init__(self, name, n, field):
        self.name = name
        self.n = n
        self.field = field

def addField():
    global editableField
    field = getField(editableField.name)
    if not field:
        field = Field(editableField.name, editableField.n, str(editableField.field))
        db.session.add(field)
    else:
        field.field = str(editableField.field)
    db.session.commit()
    editableField = None

def getField(fieldname) -> Field:
    return Field.query.filter(Field.name == fieldname).first()

class BattleField:
    name = ""
    field = []
    n = 0
    def __init__(self, name, n, field=None):
        self.name = name
        self.n = n
        if not field:
            for _ in range(n+1):
                self.field.append([0] * (n + 1))    
        else:
            self.field = field
    
    def __repr__(self) -> str:
        visualisation = ""
        for i in self.field:
            visualisation += str(i) + '\n'
        return visualisation
    
    changeId: int = 0
    def placeShip(self, x, y) -> bool:
        if self.field[x][y]:
            self.field[x][y] = 0
            self.changeId = current_milli_time()
            return True
        else:
            can_place = ((self.field[x - 1][y-1] == 0) and (self.field[x - 1][y+1] == 0) 
                    and (self.field[x + 1][y-1] == 0) and (self.field[x + 1][y+1] == 0)
                    and (self.field[x][y-1] == 0) and (self.field[x + 1][y] == 0)
                    and (self.field[x][y+1] == 0) and (self.field[x - 1][y] == 0))
            if can_place:
                self.field[x][y] = 1
                self.changeId = current_milli_time()
                return True
        return False

def getUser(username) -> User:
    return User.query.filter(User.username == username).first()


def addUser(username, password):
    user = User(username, password)
    db.session.add(user)
    db.session.commit()


def isAuthorized() -> bool:
    if "username" in session and "password" in session:
        user = getUser(session["username"])
        if user and session["password"] == user.password:
            return True
    return False


@app.route('/waiting')
def waitingScreen():
    if not isAuthorized(): return redirect(url_for('login'))
    return render_template("waiting-screen.html", username = session["username"])


@app.route('/')
def main():
    if not isAuthorized(): return redirect(url_for('login'))
    if session["username"] != "Admin":
        return redirect(url_for("waitingScreen"))
    return "Дарова, админ"
    

@app.route('/registration', methods = ["GET"])
def registration():
    if isAuthorized(): return redirect(url_for('main'))
    return render_template('registration.html')

@app.route('/registration', methods = ["POST"])
def getRegistrationData():
    username = request.form['username']
    password = request.form["password"]
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
    username = request.form['username']
    password = request.form["password"]
    user = getUser(username)
    if not user or password != user.password:
        return render_template('auth_error.html')
    session["username"] = username
    session["password"] = password
    session.permanent = True
    return redirect(url_for('waiting-screen'))


# @app.route('/logout')
# def logout():
@app.route('/creating-field', methods=['GET'])
def creatingField():
    if not isAuthorized(): return redirect(url_for('login'))
    return render_template("creating-field.html")

@app.route('/creating-field', methods=["POST"])
def getFieldSettings():
    global editableField
    fieldsize = int(request.form['fieldsize'])
    fieldname = request.form["fieldname"]
    editableField = BattleField(fieldname, fieldsize+1)
    return redirect(url_for('fieldEditing'))

@app.route('/field-editing', methods=['GET'])
def fieldEditing():
    if not isAuthorized(): return redirect(url_for('login'))
    if editableField == None: return redirect(url_for("creatingField"))
    return render_template('fieldediting.html', field=editableField.field, len=editableField.n)

@app.route('/field-editing', methods=['POST'])
def saveField():
    addField()
    return "Поле успешно сохранено"

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
    if not editableField:
        return "RELOAD"
    
    changeId: int = int(session["changeId"] if "changeId" in session else 0)
    if editableField.changeId > changeId:
        session["changeId"] = editableField.changeId
        return "UPDATE: changeId = " + str(changeId)

    return "WAIT"
    
@app.route('/fields', methods=['GET'])
def fields():
    fields = []
    for field in getField
    return render_template('view-fields.html', fields=["bebra", "bebra2", "bebra3"])

@app.route('/fields', methods=['POST'])
def getFieldButtonClick():
    global editableField
    if "play" in request.form:
        pass
    elif "edit" in request.form:
        field = getField(request.form["edit"])
        editableField = BattleField(field.name, field.n, eval(field.field))
        return redirect(url_for("fieldEditing"))
    return 'bebra'

if __name__ == '__main__':
    app.run()