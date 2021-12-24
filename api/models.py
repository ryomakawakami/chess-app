from exts import db

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(25), nullable=False, unique=True)
    email = db.Column(db.String(80), nullable=False)
    password = db.Column(db.Text(), nullable=False)

    def save(self):
        db.session.add(self)
        db.session.commit()

class Stats(db.Model):
    __tablename__ = 'stats'

    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.Integer(), db.ForeignKey(User.username), nullable=False)
    wins = db.Column(db.Integer(), default=0)
    losses = db.Column(db.Integer(), default=0)
    draws = db.Column(db.Integer(), default=0)

    user = db.relationship('User', foreign_keys='Stats.username')

    def update(self, result):
        if result == 'win':
            self.wins += 1
        elif result == 'loss':
            self.losses += 1
        else:
            self.draws += 1
        db.session.commit()

    def save(self):
        db.session.add(self)
        db.session.commit()
