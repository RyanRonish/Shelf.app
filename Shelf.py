import sys
import sqlite3
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QApplication, QWidget, QLabel, QLineEdit, QPushButton, QMessageBox, QTextEdit, QProgressBar

'''Shelf.app is a book management application. It allows users to manage their book collections, add books they've read this year, and track their current reading progress. 
Components:
User Class: Represents a user of the application. It stores user information such as username, password, name, email, and favorite genre.
Book Class: Represents a book with attributes like title, author, genre, and year of publication.
Database Class: Handles interactions with the SQLite database. It creates tables for users, books, and books read in the current year. 
Provides methods to add users, books, retrieve user information, get books, remove books, etc.
LoginSignupApp Class: GUI for user login and signup. It displays fields for entering username and password for login, or signing up with new user details. Upon successful login, it opens the main ShelfApp.
SignupApp Class: GUI for user signup. It allows users to input their name, email, username, password, and favorite genre, then signs them up and adds them to the database upon successful signup.
ShelfApp Class: Represents the main application window where users can manage their book collections. It has fields for adding, removing, searching, and listing books. 
Additionally, it displays the user's reading goal, books read in the current year, and output text area. The user can log out from here.
ShelfApplication Class: The main application class. It initializes the database and creates instances of LoginSignupApp and ShelfApp. It manages the flow between login/signup and the main ShelfApp.
Workflow:
Shelfapplication is instantiated when the application starts.
ShelfApplication initializes the database and shows the LoginSignupApp.
In LoginSignupApp, users can either log in with existing credentials or sign up with new ones.
Upon successful login, ShelfApplication switches to ShelfApp.
In ShelfApp, users can manage their book collection, add books read in the current year, track reading progress, and log out.
Users can log out from ShelfApp, which returns them to LoginSignupApp.
Next Steps.
I want to continue to make an easy to use UI for Shelf. The biggest aaaaaddition I want to make inn the future is to expand the types of collections a user can make because people don't just store books on shelves. '''

#class representing a User
class User:
    def __init__(self, username, password, name='', email='', favorite_genre=''):
        self.username = username
        self.password = password
        self.name = name
        self.email = email
        self.favorite_genre = favorite_genre

#class representing a Book
class Book:
    def __init__(self, title, author, genre, year):
        self.title = title
        self.author = author
        self.genre = genre
        self.year = year

# class representing a Database
class Database:
    def __init__(self):
        self.connection = sqlite3.connect('shelf.db')
        self.cursor = self.connection.cursor()
        self.create_tables()

    # Create necessary tables in the database
    def create_tables(self):
        # Table for storing user information
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                                username TEXT PRIMARY KEY,
                                password TEXT,
                                name TEXT,
                                email TEXT,
                                favorite_genre TEXT)''')
        # Table for storing book information
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS books (
                                title TEXT,
                                author TEXT,
                                genre TEXT,
                                year TEXT,
                                username TEXT,
                                FOREIGN KEY (username) REFERENCES users(username))''')
        # Table for storing books read in the current year
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS books_read_this_year (
                                title TEXT,
                                author TEXT,
                                genre TEXT,
                                year TEXT,
                                username TEXT,
                                FOREIGN KEY (username) REFERENCES users(username))''')  
        self.connection.commit()

    # Add a new user to the database
    def add_user(self, user):
        self.cursor.execute('''INSERT INTO users (username, password, name, email, favorite_genre)
                                VALUES (?, ?, ?, ?, ?)''',
                            (user.username, user.password, user.name, user.email, user.favorite_genre))
        self.connection.commit()

    # Retrieve user information from the database
    def get_user(self, username):
        self.cursor.execute('''SELECT * FROM users WHERE username = ?''', (username,))
        user_data = self.cursor.fetchone()
        if user_data:
            return User(user_data[0], user_data[1], user_data[2], user_data[3], user_data[4])
        else:
            return None

    # Add a new book to the database
    def add_book(self, book, username, read_this_year=False):
        if read_this_year:
            table_name = 'books_read_this_year'
        else:
            table_name = 'books'

        self.cursor.execute(f'''INSERT INTO {table_name} (title, author, genre, year, username)
                                VALUES (?, ?, ?, ?, ?)''',
                            (book.title, book.author, book.genre, book.year, username))
        self.connection.commit()

    # Retrieve books associated with a particular user from the database
    def get_books(self, username):
        self.cursor.execute('''SELECT * FROM books WHERE username = ?''', (username,))
        books_data = self.cursor.fetchall()
        books = []
        for book_data in books_data:
            books.append(Book(book_data[0], book_data[1], book_data[2], book_data[3]))
        return books
    
    # Remove a book from the database
    def remove_book(self, book_title, username):
        self.cursor.execute('''DELETE FROM books WHERE title = ? AND username = ?''', (book_title, username))
        self.connection.commit()

# Define a class representing a Login/Signup application window
class LoginSignupApp(QWidget):
    WINDOW_WIDTH = 550
    WINDOW_HEIGHT = 350

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()

    # Initialize the user interface
    def init_ui(self):
        self.setWindowTitle('Shelf - Login/Sign up')
        self.setFixedSize(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)

        self.shelf_app = None

        # Left side - Login/Signup fields
        login_layout = QVBoxLayout()
        
        # Widgets for username and password input
        self.username_label = QLabel('Username:')
        self.username_edit = QLineEdit()

        self.password_label = QLabel('Password:')
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)

        # Buttons for login and signup
        self.login_button = QPushButton('Login')
        self.login_button.clicked.connect(self.login)
        self.login_button.setFixedSize(100, 50)

        self.signup_button = QPushButton('Sign up')
        self.signup_button.clicked.connect(self.signup_window)
        self.signup_button.setFixedSize(100, 50)

        # Adjust spacing and add widgets to layout
        login_layout.addSpacing(60)
        login_layout.addWidget(self.username_label)
        login_layout.addWidget(self.username_edit)
        login_layout.addWidget(self.password_label)
        login_layout.addWidget(self.password_edit)
        login_layout.addSpacing(60)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.signup_button)
        button_layout.addStretch()
        login_layout.addLayout(button_layout)

        # Right side - Logo
        logo_layout = QVBoxLayout()
        logo_layout.addStretch()

        logo_label = QLabel()
        pixmap = QPixmap('shelf.app.png')
        logo_label.setPixmap(pixmap)
        logo_label.setAlignment(Qt.AlignCenter)

        logo_layout.addWidget(logo_label)

        # Main layout combining left and right sides
        main_layout = QHBoxLayout()
        main_layout.addLayout(login_layout)
        main_layout.addLayout(logo_layout)

        self.setLayout(main_layout)

    # Define a signal for successful login
    login_successful_signal = pyqtSignal(str)

    # Handle login process
    def login(self):
        username = self.username_edit.text()
        password = self.password_edit.text()

        user = self.db.get_user(username)
        if user:
            if user.password == password:
                self.username_edit.clear()
                self.password_edit.clear()
                self.login_successful_signal.emit(username)
                return
            else:
                QMessageBox.warning(self, 'Login Failed', 'Invalid username or password.')
        else:
            QMessageBox.warning(self, 'Login Failed', 'User not found.')

    # Open signup window
    def signup_window(self):
        self.signup_app = SignupApp(self.db, self)
        self.signup_app.show()

    # Show main shelf application window
    def show_shelf_app(self, username):
        if not self.shelf_app:
            self.shelf_app = ShelfApp(username, self.db, parent=self)
            self.shelf_app.logout_signal.connect(self.clear_shelf_app)
        else:
            self.shelf_app.clear_book_list()
        self.shelf_app.show()
    
    # Clear shelf application window
    def clear_shelf_app(self):
        self.shelf_app.clear_book_list()

    # Show login/signup window
    def show_login_signup_window(self):
        self.show()

# Define a class representing a Signup window
class SignupApp(QWidget):
    WINDOW_WIDTH = 400
    WINDOW_HEIGHT = 400

    def __init__(self, db, parent):
        super().__init__()
        self.db = db
        self.parent = parent
        self.init_ui()

    # Initialize the user interface
    def init_ui(self):
        self.setWindowTitle('Shelf - Sign up')
        self.setFixedSize(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)

        # Widgets for user information input
        self.name_label = QLabel('Name:')
        self.name_edit = QLineEdit()

        self.email_label = QLabel('Email:')
        self.email_edit = QLineEdit()

        self.username_label = QLabel('Username:')
        self.username_edit = QLineEdit()

        self.password_label = QLabel('Password:')
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)

        self.genre_label = QLabel('Favorite Genre:')
        self.genre_edit = QLineEdit()

        # Button for signup
        self.signup_button = QPushButton('Sign up')
        self.signup_button.clicked.connect(self.signup)

        # Add widgets to layout
        layout = QVBoxLayout()
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_edit)
        layout.addWidget(self.email_label)
        layout.addWidget(self.email_edit)
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_edit)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_edit)
        layout.addWidget(self.genre_label)
        layout.addWidget(self.genre_edit)
        layout.addWidget(self.signup_button)

        self.setLayout(layout)

    # Handle signup process
    def signup(self):
        name = self.name_edit.text()
        email = self.email_edit.text()
        username = self.username_edit.text()
        password = self.password_edit.text()
        favorite_genre = self.genre_edit.text()

        if not name or not email or not username or not password:
            QMessageBox.warning(self, 'Sign up Failed', 'Please fill in all the fields.')
            return

        existing_user = self.db.get_user(username)
        if existing_user:
            QMessageBox.warning(self, 'Sign up Failed', 'Username already exists. Please choose a different one.')
            return

        new_user = User(username, password, name, email, favorite_genre)
        self.db.add_user(new_user)
        QMessageBox.information(self, 'Sign up Successful', 'You have successfully signed up!')
        self.parent.show()
        self.close()

# Define a class representing the main Shelf application window
class ShelfApp(QWidget):
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600

    # Define a class-level logout signal
    logout_signal = pyqtSignal()

    def __init__(self, username, db, parent=None):
        super().__init__(parent)
        self.username = username
        self.db = db
        self.books = self.db.get_books(username)
        self.books_read_this_year = []
        self.init_ui()

    # Initialize the user interface
    def init_ui(self):
        self.setWindowTitle('Shelf - Book Collection Manager')
        self.setFixedSize(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)

        # Left side - Book management fields
        book_layout = QVBoxLayout()

        # Widgets for adding, removing, searching, and listing books
        self.title_label = QLabel('Title:')
        self.title_edit = QLineEdit()

        self.author_label = QLabel('Author:')
        self.author_edit = QLineEdit()

        self.genre_label = QLabel('Genre:')
        self.genre_edit = QLineEdit()

        self.year_label = QLabel('Year:')
        self.year_edit = QLineEdit()

        self.add_button = QPushButton('Add Book')
        self.add_button.clicked.connect(self.add_book)

        self.remove_label = QLabel('Remove Book:')
        self.remove_edit = QLineEdit()

        self.remove_button = QPushButton('Remove Book')
        self.remove_button.clicked.connect(self.remove_book)

        self.search_label = QLabel('Search Book:')
        self.search_edit = QLineEdit()

        self.search_button = QPushButton('Search Book')
        self.search_button.clicked.connect(self.search_book)

        self.list_button = QPushButton('List all Books')
        self.list_button.clicked.connect(self.list_books)

        self.quit_button = QPushButton('Log Out')
        self.quit_button.clicked.connect(self.logout)

        # Add widgets to layout
        book_layout.addWidget(self.title_label)
        book_layout.addWidget(self.title_edit)
        book_layout.addWidget(self.author_label)
        book_layout.addWidget(self.author_edit)
        book_layout.addWidget(self.genre_label)
        book_layout.addWidget(self.genre_edit)
        book_layout.addWidget(self.year_label)
        book_layout.addWidget(self.year_edit)
        book_layout.addWidget(self.add_button)
        book_layout.addWidget(self.remove_label)
        book_layout.addWidget(self.remove_edit)
        book_layout.addWidget(self.remove_button)
        book_layout.addWidget(self.search_label)
        book_layout.addWidget(self.search_edit)
        book_layout.addWidget(self.search_button)
        book_layout.addWidget(self.list_button)
        book_layout.addWidget(self.quit_button)

        # Right side - Vertical layout for reading goal, books read this year, and output text
        right_layout = QVBoxLayout()

        # Input field for adding books read this year
        input_layout = QVBoxLayout()

        input_label = QLabel('Add Book Read This Year:')
        self.input_field = QLineEdit()
        
        self.add_button = QPushButton('Add')
        self.add_button.clicked.connect(self.add_book_read_this_year)

        input_layout.addWidget(input_label)
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.add_button)

        right_layout.addLayout(input_layout)

        # Reading goal and progress bar
        goal_layout = QVBoxLayout()

        self.goal_label = QLabel('Reading Goal:')
        self.goal_value = QLabel('50 books')  # Static reading goal value

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(30)  # Example value, update dynamically based on user progress

        goal_layout.addWidget(self.goal_label)
        goal_layout.addWidget(self.goal_value)
        goal_layout.addWidget(self.progress_bar)

        right_layout.addLayout(goal_layout)

        # Books read this year
        books_read_layout = QVBoxLayout()

        books_read_label = QLabel('Books Read This Year:')
        self.books_read_text = QTextEdit()

        books_read_layout.addWidget(books_read_label)
        books_read_layout.addWidget(self.books_read_text)

        right_layout.addLayout(books_read_layout)

        # Output text
        output_layout = QVBoxLayout()

        self.output_text = QTextEdit()

        output_layout.addWidget(self.output_text)

        right_layout.addLayout(output_layout)

        # Main layout combining left and right sides
        main_layout = QHBoxLayout()
        main_layout.addLayout(book_layout)
        main_layout.addLayout(right_layout)

        self.setLayout(main_layout)

    # Show books read this year
    def show_books_read(self):
        self.books_read_text.clear()
        for book in self.books_read_this_year:
            self.books_read_text.append(f"{book.title} by {book.author}")

    # Add a book to books read this year
    def add_book_read_this_year(self):
        book_title = self.input_field.text()

        if book_title:
            book = Book(title=book_title, author='', genre='', year='')
            self.db.add_book(book, self.username, read_this_year=True)
            self.books_read_this_year.append(book)
            current_value = self.progress_bar.value()
            max_value = self.progress_bar.maximum()
            if current_value < max_value:
                self.progress_bar.setValue(current_value + 1)
            self.input_field.clear()

    # Logout and emit logout signal
    def logout(self):
        self.close()
        self.logout_signal.emit()

    # Clear book list
    def clear_book_list(self):
        self.books = []
        self.output_text.clear()

    # Add a book to the collection
    def add_book(self):
        title = self.title_edit.text()
        author = self.author_edit.text()
        genre = self.genre_edit.text()
        year = self.year_edit.text()

        new_book = Book(title, author, genre, year)
        self.db.add_book(new_book, self.username)
        self.books.append(new_book)
        self.output_text.append("Book added successfully!")
        self.clear_text_fields()

    # Remove a book from the collection
    def remove_book(self):
        title = self.remove_edit.text()
        for book in self.books:
            if book.title == title:
                self.db.remove_book(title, self.username)
                self.books.remove(book)
                self.output_text.append("Book removed successfully!")
                self.clear_text_fields()
                return
        self.output_text.append("Book not found in the collection.")
        self.clear_text_fields()

    # Search for a book in the collection
    def search_book(self):
        title = self.search_edit.text()
        for book in self.books:
            if book.title == title:
                self.output_text.append(f"Title: {book.title}, Author: {book.author}, Genre: {book.genre}, Year: {book.year}")
                return
        self.output_text.append("Book not found in the collection.")
        self.clear_text_fields()

    # List all books in the collection
    def list_books(self):
        if not self.books:
            self.output_text.append("No books in the collection.")
            return
        self.output_text.append("Listing all books:")
        for book in self.books:
            self.output_text.append(f"Title: {book.title}, Author: {book.author}, Genre: {book.genre}, Year: {book.year}")

    # Clear input fields
    def clear_text_fields(self):
        self.title_edit.clear()
        self.author_edit.clear()
        self.genre_edit.clear()
        self.year_edit.clear()
        self.remove_edit.clear()
        self.search_edit.clear()

# Define a class representing the main application
class ShelfApplication(QApplication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = Database()
        self.login_signup_app = LoginSignupApp(self.db)
        self.login_signup_app.show()
        self.login_signup_app.login_successful_signal.connect(self.show_shelf_app)

    # Show main shelf application window
    def show_shelf_app(self, username):
        self.shelf_app = ShelfApp(username, self.db)
        self.shelf_app.logout_signal.connect(self.show_login_signup_window)
        self.shelf_app.show()

    # Show login/signup window
    def show_login_signup_window(self):
        self.login_signup_app.show()

if __name__ == '__main__':
    app = ShelfApplication(sys.argv)
    sys.exit(app.exec_())
