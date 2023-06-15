from SARCI import db

class User(db.model):
    __tablename__ = 'users'

    id = db.Column(db.String, primary_key=True)
    username = db.Column(db.String, unique=True)
    password = db.Column(db.String)

    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password
    
    def __repr__(self):
        return "<User %r>" % self.username




