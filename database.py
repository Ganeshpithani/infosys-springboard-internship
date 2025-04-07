import psycopg2
import re
from psycopg2 import sql
from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST

# Connect to the database
def get_db_connection():
    """Establish a connection to the database."""
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

# Function to create the necessary tables if they do not exist
def create_table():
    """Create the necessary tables for the application if they do not exist."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Create `user_recipes` table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS user_recipes (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(100) NOT NULL,
                        ingredients TEXT NOT NULL,
                        recipe TEXT NOT NULL,
                        cooking_time VARCHAR(50),
                        nutritional_info TEXT,
                        cuisine VARCHAR(50),
                        UNIQUE(username, recipe, ingredients)
                    );
                """)

                # Create `users` table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(100) UNIQUE NOT NULL,
                        phone_no VARCHAR(15),
                        email VARCHAR(255) UNIQUE,
                        profile_picture VARCHAR(255),
                        password VARCHAR(255) NOT NULL,
                        date_of_birth DATE
                    );
                """)

                conn.commit()
                print("Tables created or verified successfully.")
    except Exception as e:
        print(f"An error occurred during table creation: {e}")

# Validate email format
def is_valid_email(email):
    """Check if the email is in a valid format."""
    return re.match(r"^[\w\.-]+@gmail\.com$", email) is not None

# Validate phone number
def is_valid_phone_number(phone_no):
    """Check if the phone number is exactly 10 digits."""
    return re.match(r"^\d{10}$", phone_no) is not None

# Function to register a new user with validation
def register_user(username, phone_no, email, profile_picture, password, date_of_birth=None):
    """Register a new user in the database, with email and phone validation."""
    
    # Email and phone number validation
    if not is_valid_email(email):
        print("Invalid email format. Only Gmail accounts are accepted.")
        return False
    
    if not is_valid_phone_number(phone_no):
        print("Invalid phone number. It must be exactly 10 digits.")
        return False

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO users (username, phone_no, email, profile_picture, password, date_of_birth)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (username, phone_no, email, profile_picture, password, date_of_birth))
                conn.commit()
                return True
    except psycopg2.IntegrityError:
        print("Error: Username or email is already in use.")
        return False
    except Exception as e:
        print(f"An error occurred during registration: {e}")
        return False

# Function to validate user login
def validate_user(username, password):
    """Validate user credentials for login."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT * FROM users WHERE username = %s AND password = %s
                """, (username, password))
                return cur.fetchone() is not None
    except Exception as e:
        print(f"An error occurred during login validation: {e}")
        return False

# Insert recipe into the database
def insert_recipe(username, recipe_name, cooking_time, cuisine, ingredients, nutritional_info, recipe_text):
    """Insert a new recipe into the user_recipes table."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO user_recipes (username, recipe, ingredients, cooking_time, nutritional_info, cuisine)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (username, recipe_text, ingredients, cooking_time, nutritional_info, cuisine))
                conn.commit()
                return True
    except psycopg2.IntegrityError:
        print("Error: Duplicate recipe entry.")
        return False
    except Exception as e:
        print(f"An error occurred while inserting recipe: {e}")
        return False

# Fetch user details
def get_user_details(username):
    """Retrieve user details based on username."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT username, phone_no, email, profile_picture, date_of_birth FROM users WHERE username = %s
                """, (username,))
                user = cur.fetchone()
                if user:
                    return {
                        "username": user[0],
                        "phone_no": user[1],
                        "email": user[2],
                        "profile_picture": user[3],
                        "date_of_birth": user[4]
                    }
                else:
                    print("User not found.")
                    return None
    except Exception as e:
        print(f"An error occurred while fetching user details: {e}")
        return None
    
def get_user_recipes(username):
    """Retrieve all recipes saved by a specific user."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT recipe, ingredients, cooking_time, nutritional_info, cuisine 
                    FROM user_recipes WHERE username = %s
                """, (username,))
                recipes = cur.fetchall()
                return [
                    {
                        "name": recipe[0],
                        "ingredients": recipe[1],
                        "cooking_time": recipe[2],
                        "nutritional_info": recipe[3],
                        "cuisine": recipe[4],
                    }
                    for recipe in recipes
                ]
    except Exception as e:
        print(f"An error occurred while fetching recipes: {e}")
        return []


# Call create_table when the script is run
if __name__ == "__main__":
    create_table()  
