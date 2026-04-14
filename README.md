# Smart Recipe Generator

This project is a web-based application that generates recipes using images of ingredients. The system detects ingredients from uploaded images and automatically creates a complete recipe using AI.

It is built using Python, Streamlit, Computer Vision, and NLP techniques.

---

## Project Overview

The main idea of this project is simple:

Instead of typing ingredients manually, the user uploads images of food items.  
The system reads those images, identifies ingredients, and generates a recipe.

The application also allows users to register, log in, and save their favorite recipes.

---

## Features

- User registration and login system  
- Upload images of ingredients  
- Extract text from images using OCR  
- Detect ingredients using AI models  
- Generate recipes using OpenAI  
- Save and view previously generated recipes  
- Store user data and recipes in PostgreSQL database  

---

## How the System Works

### Step 1: Image Upload  
User uploads images of ingredients.

### Step 2: Image Processing  
The system processes images using OpenCV.

### Step 3: Text Extraction  
OCR tools like Tesseract and EasyOCR extract text from images.

### Step 4: Ingredient Detection  
The extracted text is cleaned and passed to AI to identify actual ingredients.

If text is not found, image classification is used.

### Step 5: Recipe Generation  
Ingredients are sent to OpenAI API to generate a complete recipe.

### Step 6: Save Recipe  
User can store the recipe in the database.

---

## Project Structure

- config.py  
  Stores environment variables like database credentials and API keys.

- database.py  
  Handles database connection and operations such as:
  - Creating tables  
  - User registration  
  - Login validation  
  - Saving recipes  
  - Fetching user data  

- image.py  
  Handles image processing and ingredient detection:
  - Preprocessing images  
  - OCR using Tesseract and EasyOCR  
  - Image classification using Transformers  
  - Ingredient extraction using OpenAI  

- main.py  
  Main application file using Streamlit:
  - UI design  
  - User authentication  
  - Image upload  
  - Recipe generation  
  - Display and save recipes  

---

## Technologies Used

- Python  
- Streamlit  
- OpenCV  
- EasyOCR  
- Tesseract OCR  
- PyTorch  
- Transformers  
- OpenAI API  
- PostgreSQL  
- NumPy  
- Pandas  

---

## Requirements

Install all dependencies using:

pip install -r requirements.txt

Main libraries used:

- torch  
- torchvision  
- transformers  
- streamlit  
- opencv-python-headless  
- easyocr  
- pytesseract  
- psycopg2-binary  
- openai  
- numpy  
- pandas  

---

## Environment Variables

Create a `.env` file and add the following:

DB_NAME=your_database_name  
DB_USER=your_database_user  
DB_PASSWORD=your_password  
DB_HOST=your_host  
DB_PORT=your_port  
OPENAI_API_KEY=your_api_key  

---

## How to Run the Project

1. Install dependencies  
2. Set up PostgreSQL database  
3. Add `.env` file  
4. Run the application  

streamlit run main.py  

---

## Database Tables

### Users Table
Stores user details:
- username  
- email  
- phone number  
- password  
- date of birth  

### User Recipes Table
Stores recipes:
- username  
- ingredients  
- recipe  
- cooking time  
- nutrition info  
- cuisine  

---

## Important Notes

- Email validation accepts only Gmail accounts  
- Phone number must be exactly 10 digits  
- Duplicate recipes are not allowed  
- Model fallback is used if OCR fails  

---

## Future Improvements

- Add more accurate food detection models  
- Support more languages in OCR  
- Improve UI design  
- Add recommendation system  
- Deploy on cloud  

---

## Author

Pithani Ganesh  

Infosys Springboard Internship Project  
