from flask import Flask, request
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///books.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
api = Api(app)
bcrypt = Bcrypt(app)

# Define a pre-defined password for updates and deletions
ADMIN_PASSWORD_HASH = bcrypt.generate_password_hash("admin123").decode("utf-8")


#                                           MIDDLEWARES
# Define a decorator for admin access
def user_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        username = request.json.get("username")
        password = request.json.get("password")

        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            return {"error": "Unauthorized access"}, 401
        return f(*args, **kwargs)

    return decorated_function


# Define a decorator for registration access
def admin_check(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        admin_username = request.json.get("username")
        admin_password = request.json.get("password")

        admin_user = User.query.filter_by(username=admin_username).first()
        if (
            not admin_user
            or not admin_user.check_password(admin_password)
            or admin_user.role != "admin"
        ):
            return {"error": "Only admins can register users"}, 401
        return f(*args, **kwargs)

    return decorated_function

#                                           DATABASES
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def serialize(self):
        return {"id": self.id, "username": self.username, "role": self.role}


class Books(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)

    def serialize(self):
        return {"id": self.id, "title": self.title, "author": self.author}

#                                           ROUTES

class Auth(Resource):

    # Register
    @admin_check
    def post(self):
        data = request.json
        new_user = data.get("user")

        # Extract new user details
        new_username = new_user.get("username")
        new_password = new_user.get("password")
        role = new_user.get("role", "user")

        # Check if the new username already exists
        if User.query.filter_by(username=new_username).first():
            return {"error": "Username already exists"}, 400

        # Create and add new user
        new_user = User(username=new_username, role=role)
        new_user.set_password(new_password)
        db.session.add(new_user)
        db.session.commit()
        return {"msg": "User created successfully"}, 201

    # Login
    @user_auth
    def get(self):
        data = request.json
        username = data.get("username")
        user = User.query.filter_by(username=username).first()
        return user.serialize(), 200


    # edit user
    @user_auth
    def put(self):
        data = request.json.get("user")
        new_username = data.get("username")
        new_password = data.get("password")

        username = request.json.get("username")
        user = User.query.filter_by(username=username).first()
        user.username = new_username
        user.set_password(new_password)

        db.session.commit()
        return user.serialize(), 200


class BookList(Resource):
    
    def get(self):
        books = Books.query.all()
        books_data = [book.serialize() for book in books]
        return {"books": books_data}

    @user_auth
    def post(self):
        data = request.json
        title = data.get("title")
        author = data.get("author")

        if not title or not author:
            return {"error": "Title and author are required"}, 400

        new_book = Books(title=title, author=author)
        db.session.add(new_book)
        db.session.commit()
        return {"msg": f"Book {title} added!"}, 201


class Book(Resource):
    
    def get(self, book_id):
        book = Books.query.get(book_id)
        if book:
            return book.serialize(), 200
        else:
            return {"error": "Book not found"}, 404

    @user_auth
    def put(self, book_id):
        data = request.json
        title = data.get("title")
        author = data.get("author")

        book = Books.query.get(book_id)
        if book:
            book.title = title or book.title
            book.author = author or book.author
            db.session.commit()
            return book.serialize(), 200
        else:
            return {"error": "Book not found"}, 404

    @user_auth
    def delete(self, book_id):
        book = Books.query.get(book_id)
        if book:
            db.session.delete(book)
            db.session.commit()
            return {"msg": "Book deleted successfully"}, 200
        else:
            return {"error": "Book not found"}, 404


api.add_resource(Auth, "/auth")
api.add_resource(BookList, "/books")
api.add_resource(Book, "/books/<int:book_id>")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)