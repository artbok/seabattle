import os
from flask import Flask, render_template, request, url_for, redirect, session, jsonify
from flask_sqlalchemy import SQLAlchemy


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "456jk456gjkdfugi734fuhu83ceji"

db = SQLAlchemy(app)


class User(db.Model):
    username = db.Column(db.String, primary_key=True)
    password = db.Column(db.String)
    is_admin = db.Column(db.Boolean)

    def __init__(self, username, password, is_admin):
        self.username = username
        self.password = password
        is_admin = is_admin

    def __repr__(self):
        return f'<User {self.username} {self.password} {self.is_admin}>'

class BattleField:
    field = []
    def __init__(self, n):
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
                    and (self.field[x][y+1]) and (self.field[x - 1][y] == 0))
            if can_place:
                self.field[x][y] = 1
                return True
            return False


def getUser(username) -> User:
    return User.query.get(username)

def addUser(username, password, is_admin):
    user = User(username, password, is_admin)
    db.session.add(user)
    db.session.commit()

battleField: BattleField = None
def genField(n):
    global battleField
    if battleField:
        return battleField.field
    battleField = BattleField(10)
    return battleField.field

@app.route('/registration', methods = ["GET"])
def registration():
    return render_template('registration.html')

@app.route('/registration', methods = ["POST"])
def getRegistrationData():
    username = request.form['username']
    password = request.form["password"]
    role = True if request.form["is_admin"] == "admin" else False
    if getUser(username):
        return "Account with that username already exists!"
    addUser(username, password, role)
    return 'Account was successfully created!'

@app.route('/')
def redirectToLogin():
    # code = genField(10)
    # return render_template('test.html', matrix=code)
    return redirect(url_for('login'))

@app.route('/login', methods = ['GET'])
def login():
    return render_template("authorization.html")

@app.route('/login', methods = ['POST'])
def getLoginData():
    username = request.form['username']
    password = request.form["password"]
    user = getUser(username)
    if not user or password != user.password:
        return render_template('auth_error.html')
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
@app.route('/field-editing', methods=['GET'])
def fieldEditing():
    return render_template('fieldediting.html', field=genField(10), len=10)
@app.route('/field-cell-update', methods = ['POST'])
def cellUpdate():
    data = request.json
    x = data['x']
    y = data['y']
    value = data['val']
    battleField.field[x][y] = value
    return ""

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