import streamlit as st
import os
import base64
from database import create_table, register_user, validate_user, insert_recipe, get_user_details, get_user_recipes
from image import process_uploaded_images
from config import OPENAI_API_KEY
import openai
import time
from PIL import Image
import io

# Set the page configuration
st.set_page_config(page_title="Smart Recipe Generator", layout="wide")

def load_css():
    """Load custom CSS styles."""
    try:
        with open("static/style.css") as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"Could not load CSS: {str(e)}")

def safe_load_image(image_path):
    """Safely load an image file with error handling."""
    try:
        if isinstance(image_path, str) and os.path.exists(image_path):
            return Image.open(image_path)
        elif isinstance(image_path, (bytes, io.BytesIO)):
            return Image.open(io.BytesIO(image_path))
        return None
    except Exception as e:
        st.warning(f"Could not load image: {str(e)}")
        return None

def set_background_image():
    """Set background image with error handling."""
    image_path = "static/12.png"
    try:
        if os.path.exists(image_path):
            with open(image_path, "rb") as image_file:
                image_base64 = base64.b64encode(image_file.read()).decode()
                st.markdown(
                    f"""
                    <style>
                    .stApp {{
                        background-image: url("data:image/png;base64,{image_base64}");
                        background-size: cover;
                        background-position: center;
                        background-repeat: no-repeat;
                        background-attachment: fixed;
                        width: 100vw;
                        height: 100vh;
                        overflow: hidden;
                    }}
                    </style>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.warning("Background image not found. Using default background.")
    except Exception as e:
        st.warning(f"Error loading background image: {str(e)}")

def format_ingredients(ingredients):
    """Format ingredients list to string."""
    if isinstance(ingredients, list):
        return ", ".join(ingredients)
    return str(ingredients)

def generate_recipe(ingredients, diet_preference):
    """Generate recipe using OpenAI API."""
    ingredients_str = format_ingredients(ingredients)
    prompt = (
        f"Create a detailed recipe using these ingredients: {ingredients_str}. "
        f"Make sure the recipe is {diet_preference}. "
        "Provide the following information in markdown format: "
        "**Recipe Name:**\n"
        "**Cooking Time:**\n"
        "**Cuisine:**\n"
        "**Ingredients:**\n"
        "**Nutritional Information:**\n"
        "**Instructions:**\n"
        "Format your response clearly with bold text for subheadings."
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        st.error(f"Error generating recipe: {e}")
        return None

def display_generated_recipe(recipe_text):
    """Display the generated recipe with proper formatting."""
    if recipe_text:
        st.write("### Generated Recipe")
        st.markdown(recipe_text)
    else:
        st.error("Recipe generation failed. Please try again.")
def extract_recipe_details(recipe_text):
    """Extract structured data from generated recipe text."""
    lines = recipe_text.split('\n')
    recipe_details = {
        "name": "",
        "cooking_time": "",
        "cuisine": "",
        "nutritional_info": "",
        "instructions": ""
    }
    current_section = None
    nutritional_info_lines = []
    instructions_lines = []

    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        if line.startswith("**Recipe Name:**"):
            # Extract only the recipe name part
            recipe_details["name"] = line.split(" ")[-1].strip()
            current_section = None
        elif line.startswith("**Cooking Time:**"):
            recipe_details["cooking_time"] = line.split("**Cooking Time:**")[-1].strip()
            current_section = None
        elif line.startswith("**Cuisine:**"):
            recipe_details["cuisine"] = line.split("**Cuisine:**")[-1].strip()
            current_section = None
        elif line.startswith("**Nutritional Information:**"):
            current_section = "nutritional_info"
        elif line.startswith("**Instructions:**"):
            current_section = "instructions"
        elif current_section == "nutritional_info":
            nutritional_info_lines.append(line)
        elif current_section == "instructions":
            instructions_lines.append(line)

    recipe_details["nutritional_info"] = " ".join(nutritional_info_lines).strip()
    recipe_details["instructions"] = "\n".join(instructions_lines).strip()
    
    return recipe_details

def handle_profile_picture_display(user_details):
    """Handle profile picture display with proper error handling."""
    try:
        if user_details and 'profile_picture' in user_details and user_details['profile_picture']:
            image = safe_load_image(user_details['profile_picture'])
            if image:
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format='PNG')
                img_byte_arr = img_byte_arr.getvalue()
                st.sidebar.image(img_byte_arr, width=150)
            else:
                raise ValueError("Could not load profile picture")
        else:
            default_path = "static/2.png"
            if os.path.exists(default_path):
                st.sidebar.image(default_path, width=150)
            else:
                st.sidebar.warning("Default profile picture not found")
    except Exception as e:
        st.sidebar.warning("Could not load profile picture")
        try:
            st.sidebar.image("static/2.png", width=150)
        except:
            st.sidebar.warning("Unable to load any profile picture")

def handle_profile_picture_upload(profile_picture):
    """Handle profile picture upload with validation."""
    try:
        if profile_picture:
            img_bytes = profile_picture.read()
            try:
                Image.open(io.BytesIO(img_bytes))
                return img_bytes
            except Exception as e:
                st.error("Invalid image file. Please upload a valid image.")
                return None
        return None
    except Exception as e:
        st.error(f"Error processing profile picture: {str(e)}")
        return None

def main():
    load_css()
    set_background_image()
    create_table()

    # Initialize session state variables
    if "page" not in st.session_state:
        st.session_state.page = "landing"
    if "ingredients_identified" not in st.session_state:
        st.session_state.ingredients_identified = []
    if "diet_preference" not in st.session_state:
        st.session_state.diet_preference = "Vegetarian"
    if "recipe_saved" not in st.session_state:
        st.session_state.recipe_saved = False

    # Landing Page
    if st.session_state.page == "landing":
        st.markdown('<div class="container">', unsafe_allow_html=True)
        st.markdown('<h1 class="animated-text">Welcome to Smart Recipe Generator!</h1>', unsafe_allow_html=True)
        st.markdown('<h3 class="animated-subtitle">Create Delicious Recipes using the ingredients you have at home</h3>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Login", key="login_button"):
                st.session_state.page = "login"
        with col2:
            if st.button("Register", key="register_button"):
                st.session_state.page = "register"
        st.markdown('</div>', unsafe_allow_html=True)

    # Login Page
    elif st.session_state.page == "login":
        st.markdown('<div class="container">', unsafe_allow_html=True)
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login", key="login_submit"):
            if validate_user(username, password):
                st.session_state.logged_in_user = username
                st.session_state.page = "main"
                st.success("Login successful!")
            else:
                st.error("Invalid username or password.")
        
        if st.button("Back to Home", key="login_home"):
            st.session_state.page = "landing"
        st.markdown('</div>', unsafe_allow_html=True)

    # Registration Page
    elif st.session_state.page == "register":
        st.markdown('<div class="container">', unsafe_allow_html=True)
        st.subheader("Registration")
        
        username = st.text_input("Username", key="register_username")
        phone_no = st.text_input("Phone Number", key="register_phone")
        email = st.text_input("Email", key="register_email")
        profile_picture = st.file_uploader("Profile Picture", type=["jpg", "png", "jpeg"], key="register_profile_picture")
        date_of_birth = st.date_input("Date of Birth", help="Select your date of birth.")
        password = st.text_input("Password", type="password", key="register_password")
        
        if st.button("Register", key="register_submit"):
            profile_picture_data = handle_profile_picture_upload(profile_picture)
            if register_user(username, phone_no, email, profile_picture_data, password, date_of_birth):
                st.success("Registration successful! Redirecting to login...")
                time.sleep(2)
                st.session_state.page = "login"
            else:
                st.error("Registration failed. Username or email might already exist.")
        
        if st.button("Back to Home", key="register_home"):
            st.session_state.page = "landing"
        st.markdown('</div>', unsafe_allow_html=True)

    # Main Application Page
    elif st.session_state.page == "main" and "logged_in_user" in st.session_state:
        st.sidebar.title("Your Account")
        user_details = get_user_details(st.session_state.logged_in_user)
        handle_profile_picture_display(user_details)

        if user_details:
            st.sidebar.subheader(user_details["username"])
            st.sidebar.write(f"**Email:** {user_details['email']}")
            st.sidebar.write(f"**Phone No:** {user_details['phone_no']}")
            st.sidebar.write(f"**Date of Birth:** {user_details['date_of_birth']}")
        else:
            st.sidebar.write("User details not found.")

        if st.sidebar.button("Logout", key="logout"):
            st.session_state.page = "landing"
            st.session_state.logged_in_user = None
            st.session_state.ingredients_identified = []

        tab1, tab2 = st.tabs(["🧑‍🍳 Recipe Generation", "📚 Saved Recipes"])

        with tab1:
            st.title("Recipe Generation")
            st.session_state.diet_preference = st.selectbox(
                "Select Diet Preference:",
                ["Vegetarian", "Non-Vegetarian"],
                index=0
            )

            uploaded_files = st.file_uploader(
                "Upload images of ingredients",
                type=["jpg", "png", "jpeg"],
                accept_multiple_files=True
            )

            if uploaded_files and st.button("Identify Ingredients", key="identify_ingredients"):
                image_paths = []
                for uploaded_file in uploaded_files:
                    temp_path = f"temp_{uploaded_file.name}"
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    image_paths.append(temp_path)

                st.session_state.ingredients_identified = process_uploaded_images(image_paths)
                st.success("Ingredients identified successfully!")

                for path in image_paths:
                    try:
                        os.remove(path)
                    except:
                        pass

            if st.session_state.ingredients_identified:
                st.write("Identified Ingredients:", st.session_state.ingredients_identified)
                
                if st.button("Generate Recipe", key="generate_recipe"):
                    recipe_text = generate_recipe(
                        st.session_state.ingredients_identified,
                        st.session_state.diet_preference
                    )
                    st.session_state.generated_recipe_text = recipe_text
                    st.session_state.recipe_saved = False
                    display_generated_recipe(recipe_text)
                
                if 'generated_recipe_text' in st.session_state and st.session_state.generated_recipe_text:
                    if st.button("Generate New Recipe", key="generate_new_recipe"):
                        new_recipe_text = generate_recipe(
                            st.session_state.ingredients_identified,
                            st.session_state.diet_preference
                        )
                        st.session_state.generated_recipe_text = new_recipe_text
                        st.session_state.recipe_saved = False
                        display_generated_recipe(new_recipe_text)

                    if not st.session_state.recipe_saved and st.button("Save Recipe", key="save_recipe"):
                        recipe_details = extract_recipe_details(st.session_state.generated_recipe_text)
                        ingredients = format_ingredients(st.session_state.ingredients_identified)
                        
                        if insert_recipe(
                            st.session_state.logged_in_user,
                            recipe_details["name"],
                            recipe_details["cooking_time"],
                            recipe_details["cuisine"],
                            ingredients,
                            recipe_details["nutritional_info"],
                            st.session_state.generated_recipe_text
                        ):
                            st.success("Recipe saved successfully!")
                            st.session_state.recipe_saved = True
                        else:
                            st.error("Failed to save recipe. Please try again.")

        with tab2:
            st.title("Saved Recipes")
            saved_recipes = get_user_recipes(st.session_state.logged_in_user) or []
            
            if not saved_recipes:
                st.info("You have no saved recipes.")
            else:
                recipe_names = [recipe["name"] for recipe in saved_recipes]
                selected_recipe_name = st.selectbox("Select a recipe to view details", recipe_names)
                if selected_recipe_name:
                    selected_recipe = next((r for r in saved_recipes if r["name"] == selected_recipe_name), None)
                    if selected_recipe:
                        st.subheader(selected_recipe["name"])
                        st.write(f"**Cooking Time:** {selected_recipe['cooking_time']}")
                        st.write(f"**Cuisine:** {selected_recipe['cuisine']}")
                        st.write(f"**Ingredients:**\n{selected_recipe['ingredients']}")
                        st.write(f"**Nutritional Info:**\n{selected_recipe['nutritional_info']}")
                       
                    else:
                        st.warning("Selected recipe not found.")

if __name__ == "__main__":
    main()
