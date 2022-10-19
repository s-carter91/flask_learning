from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import date, timedelta
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import JWTManager, create_access_token

app = Flask(__name__)

app.config ['JSON_SORT_KEYS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://tello_dev:password123@127.0.0.1:5432/trello'
app.config['JWT_SECRET_KEY'] = 'hello there'

db = SQLAlchemy(app)
ma = Marshmallow(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    email = db.Column(db.String, nullable=False, unique = True)
    password = db.Column(db.String, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'email', 'password', 'is_admin')


class Card(db.Model):
    __tablename__ = 'cards'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    date = db.Column(db.Date)
    status = db.Column(db.String)
    priority = db.Column(db.String)

class CardSchema(ma.Schema):
    class Meta:
        fields = ('id', 'title', 'description', 'status', 'priority', 'date')
        ordered = True


# Define a custom CLI (terminal) command
@app.cli.command('create')
def create_db():
    db.create_all()
    print("Tables created")

@app.cli.command('drop')
def drop_db():
    db.drop_all()
    print("Tables dropped")

@app.cli.command('seed')
def seed_db():
    users = [
        User(
            email = 'admin@spam.com',
            password = bcrypt.generate_password_hash('eggs').decode('utf-8'),
            is_admin = True
        ),
        User(
            name = 'John Cleese',
            email = 'someone@spam.com',
            password = bcrypt.generate_password_hash('12345').decode('utf-8'),
        ),
    ]

    cards = [
        Card(
            title = 'Start the project',
            description = 'Stage 1 - Create the database',
            status = 'To Do',
            priority = 'High',
            date = date.today()
        ),
        Card(
            title = "SQLAlchemy",
            description = "Stage 2 - Integrate ORM",
            status = "Ongoing",
            priority = "High",
            date = date.today()
        ),
        Card(
            title = "ORM Queries",
            description = "Stage 3 - Implement several queries",
            status = "Ongoing",
            priority = "Medium",
            date = date.today()
        ),
        Card(
            title = "Marshmallow",
            description = "Stage 4 - Implement Marshmallow to jsonify models",
            status = "Ongoing",
            priority = "Medium",
            date = date.today()
        )
    ]

    db.session.add_all(cards)
    db.session.add_all(users)
    # Have to commit after adding
    db.session.commit()
    print('Tables seeded')

@app.route('/auth/register/', methods = ['POST'])
def auth_register():
    try:
        #  Create a new User model instance from the user_info
        user = User(
            email = request.json['email'],
            password = bcrypt.generate_password_hash(request.json['password']).decode('utf-8'),
            name = request.json['name']
        )
        # Add and commit user to DB
        db.session.add(user)
        db.session.commit()
        # Respond to client
        return UserSchema(exclude=['password']).dump(user), 201
    except IntegrityError:
        return {'error': 'Email address already in use'}, 409

@app.route('/auth/login/', methods=['POST'])
def auth_login():
    # Find a user by email address
    stmt = db.select(User).filter_by(email=request.json['email'])
    user = db.session.scalar(stmt)
    # Check users password against email address
    if user and bcrypt.check_password_hash(user.password, request.json['password']):
        token = create_access_token(identity=str(user.id), expires_delta=timedelta(days=1))
        return {'email': user.email, 'token': token, 'is_admin': user.is_admin}
    else:
        return {'error': 'Invalid email or password'}, 401

@app.route('/cards/')
def all_cards():
    #select * from cards;
    # cards = Card.query.all()
    # print(cards.__dict__)
    stmt = db.select(Card).order_by(Card.priority, Card.title)
    cards = db.session.scalars(stmt)
    return CardSchema(many=True).dump(cards)
    # print(cards[0].__dict__)

@app.cli.command('first_card')
def first_card():
    # card = Card.query.first()
    # print(card[0].__dict__)
    stmt = db.select(Card).limit(1)
    card = db.session.scalar(stmt)
    print(card.__dict__)

app.cli.command('count_ongoing')
def count_ongoing():
    stmt = db.select(db.func.count()).select_from(Card).filter_by(status='Ongoing')
    cards = db.session.scalar(stmt)
    print(cards)

@app.route('/')
def index():
    return "Hello World!"