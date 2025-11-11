# 🍳 Smart Recipe Generator

The **Smart Recipe Generator** is an AI-powered web application that suggests personalized recipes based on the ingredients available to the user.  
It uses **Machine Learning** and **Natural Language Processing (NLP)** to generate intelligent and creative recipe ideas.  
The frontend is built using **Streamlit** for a clean and interactive user experience.

---

## 🚀 Features

- 🧠 Suggests recipes using AI (based on available ingredients)
- 🍴 Provides step-by-step cooking instructions
- 👤 Gives personalized recommendations based on user preferences
- 🧾 Supports text and image input for ingredients (through OCR)
- 💾 Connects with a database to store user and recipe data
- 💡 Simple and user-friendly Streamlit interface

---

## 🧰 Tech Stack

| Area | Technology Used |
|------|------------------|
| **Frontend** | Streamlit |
| **Backend** | Python, Flask / FastAPI (optional) |
| **AI / NLP** | OpenAI API |
| **Database** | PostgreSQL |
| **OCR (Image to Text)** | Tesseract, EasyOCR, OpenCV |
| **Environment Management** | Python-dotenv |
| **Machine Learning** | PyTorch, NumPy, Pandas |

---

## 🗂️ Project Structure

Smart_Recipe_Generator/
│
├── app.py # Main Streamlit app file
├── config.py # Loads API keys and database credentials
├── database.py # Handles database connections and queries
├── recipe_generator.py # AI logic for generating recipes
├── requirements.txt # All dependencies
├── .env # Environment variables (not shared publicly)
└── README.md # Project documentation


How It Works:
The user enters available ingredients (text or image).
The system uses OCR (EasyOCR or Tesseract) to extract text from images if needed.
The AI model (OpenAI API) generates personalized recipes using the ingredients.
Recipes are displayed in the Streamlit interface with instructions and suggestions.
Data can be stored in the PostgreSQL database for future use.



