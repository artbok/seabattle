import os
from flask import Flask, render_template, request, url_for, redirect, session, jsonify
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
    def __init__(self, field):
        self.field = field


class BattleField:
    name = ""
    field = []
    n = 0
    def __init__(self, name, n):
        self.name = name
        self.n = n
        for _ in range(n+1):
            self.field.append([0] * (n + 1))    
    
    def __repr__(self) -> str:
        visualisation = ""
        for i in self.field:
            visualisation += str(i) + '\n'
        return visualisation
    def place_ship(self, x, y) -> bool:
        if self.field[x][y]:
            self.field[x][y] = 0
            return True
        else:
            can_place = ((self.field[x - 1][y-1] == 0) and (self.field[x - 1][y+1] == 0) 
                    and (self.field[x + 1][y-1] == 0) and (self.field[x + 1][y+1] == 0)
                    and (self.field[x][y-1] == 0) and (self.field[x + 1][y] == 0)
                    and (self.field[x][y+1] == 0) and (self.field[x - 1][y] == 0))
            if can_place:
                self.field[x][y] = 1
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

@app.route('/')
def main():
    if not isAuthorized(): return redirect(url_for('login'))
    return "You're logged!"
    

@app.route('/registration', methods = ["GET"])
def registration():
    if isAuthorized(): 
        return redirect(url_for('main'))
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
    return 'Account was successfully created!'


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
    return "Успешная авторизация!"
    # if session["username"]:
    #     user = getUser(session["username"])
    #     if user.password != session["password"]:
    #         session["username"] = ""
    #         session["password"] = ""
    #         return auth page
    #     else success
    # return auth page

    # db.drop_all()
    # db.create_all()
    # user = User("Petya", "12345", False)
    # db.session.add(user)
    # db.session.commit()
    #print(getUser("Petya"))
#@app.route('/cookie')
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

@app.route('/field-cell-update', methods = ['POST'])
def cellUpdate():
    data = request.json
    x = data['x']
    y = data['y']
    if editableField.place_ship(x, y):
        return ""
    else:
        return "error"

# @app.route('/register', methods=['POST'])
# def register_post():
#     username = request.form.get('username')
#     password = request.form.get('password')
#     #role = True if request.form.get('remember') else False

#     user = User.query.filter_by(email=email).first()

#     # check if the user actually exists
#     # take the user-supplied password, hash it, and compare it to the hashed password in the database
#     if not user or not check_password_hash(user.password, password):
#         flash('Please check your login details and try again.')
#         return redirect(url_for('auth.login')) # if the user doesn't exist or password is wrong, reload the page

#     # if the above check passes, then we know the user has the right credentials
#     return redirect(url_for('main.profile'))
if __name__ == '__main__':
    app.run()