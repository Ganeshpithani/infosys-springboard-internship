import cv2
import numpy as np
import os
import re
import openai
from PIL import Image
import pytesseract
import easyocr
import torch

# Defer PyTorch imports to runtime with error handling
def load_ml_dependencies():
    try:
        import torch
        import torchvision.transforms as transforms
        from transformers import AutoModelForImageClassification, AutoImageProcessor
        return True, (torch, transforms, AutoModelForImageClassification, AutoImageProcessor)
    except Exception as e:
        print(f"Error loading ML dependencies: {str(e)}")
        return False, None

class ImageProcessor:
    def __init__(self):
        self.model = None
        self.image_processor = None
        self.labels = []
        self.ml_enabled = False
        self.setup_ml()

    def setup_ml(self):
        success, modules = load_ml_dependencies()
        if success:
            torch, transforms, AutoModelForImageClassification, AutoImageProcessor = modules
            try:
                model_name = "jazzmacedo/fruits-and-vegetables-detector-36"
                self.model = AutoModelForImageClassification.from_pretrained(model_name)
                self.image_processor = AutoImageProcessor.from_pretrained(model_name)
                self.model.eval()
                self.labels = list(self.model.config.id2label.values())
                self.ml_enabled = True
                
                # Define preprocessing pipeline
                self.preprocess = transforms.Compose([
                    transforms.Resize((224, 224)),
                    transforms.ToTensor(),
                    transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                                      std=[0.229, 0.224, 0.225])
                ])
            except Exception as e:
                print(f"Error setting up ML model: {str(e)}")
                self.ml_enabled = False
        else:
            self.ml_enabled = False

    def preprocess_image(self, image):
        try:
            resized_image = cv2.resize(image, (224, 224))
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)
            thresh_image = cv2.adaptiveThreshold(
                blurred_image, 255, 
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            kernel = np.ones((3, 3), np.uint8)
            processed_image_for_ocr = cv2.morphologyEx(
                thresh_image, 
                cv2.MORPH_CLOSE, 
                kernel
            )
            return resized_image, processed_image_for_ocr
        except Exception as e:
            print(f"Error preprocessing image: {str(e)}")
            return None, None

    def perform_ocr(self, processed_image_for_ocr, original_image):
        try:
            # Tesseract OCR
            tesseract_text = pytesseract.image_to_string(processed_image_for_ocr)
            cleaned_tesseract_text = self.clean_text(tesseract_text)

            # EasyOCR
            reader = easyocr.Reader(['en'])
            easyocr_text = reader.readtext(original_image, detail=0)
            cleaned_easyocr_text = [self.clean_text(text) for text in easyocr_text]

            return cleaned_tesseract_text, cleaned_easyocr_text
        except Exception as e:
            print(f"Error performing OCR: {str(e)}")
            return "", []

    def classify_image(self, resized_image):
        if not self.ml_enabled:
            return "unknown", 0.0

        try:
            # Convert BGR to RGB
            rgb_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_image)
            
            # Process image
            inputs = self.image_processor(pil_image, return_tensors="pt")
            
            with torch.no_grad():
                outputs = self.model(**inputs)

            predicted_idx = outputs.logits.argmax(-1).item()
            probs = torch.softmax(outputs.logits, dim=-1)
            confidence = probs[0][predicted_idx].item()
            predicted_label = self.model.config.id2label[predicted_idx]

            return predicted_label, confidence
        except Exception as e:
            print(f"Error classifying image: {str(e)}")
            return "unknown", 0.0

    @staticmethod
    def clean_text(text):
        cleaned_text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        return cleaned_text.strip()

    def identify_food_ingredients(self, text_list):
        ingredients = []
        base_prompt = """
        Analyze this text and determine if it contains a food ingredient name. 
        Rules:
        - Return ONLY the ingredient name if found
        - Ignore brand names, quantities, packaging info, or cooking instructions
        - If there are multiple ingredients in one text, return only the main ingredient
        
        Text to analyze: '{}'
        """
        
        for text in text_list:
            if text.strip():
                try:
                    prompt = base_prompt.format(text)
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are a food ingredient identifier. Respond only with the ingredient name, or 'none' if no ingredient is found."},
                            {"role": "user", "content": prompt}
                        ]
                    )
                    ingredient = response['choices'][0]['message']['content'].strip().lower()
                    if ingredient and ingredient != "none":
                        ingredient = re.sub(r'(diced|sliced|fresh)\s+', '', ingredient)
                        ingredients.append(ingredient)
                except Exception as e:
                    print(f"Error identifying ingredient from text: {str(e)}")
                    continue
        
        return list(set(sorted(ingredients)))

def process_uploaded_images(image_paths):
    processor = ImageProcessor()
    all_ingredients = []

    for image_path in image_paths:
        try:
            if not os.path.exists(image_path):
                print(f"Error: File {image_path} does not exist.")
                continue
            
            image = cv2.imread(image_path)
            if image is None:
                print(f"Error: Could not load image {image_path}")
                continue
            
            resized_image, processed_image_for_ocr = processor.preprocess_image(image)
            if resized_image is None or processed_image_for_ocr is None:
                continue

            cleaned_tesseract_text, cleaned_easyocr_text = processor.perform_ocr(
                processed_image_for_ocr, 
                image
            )
            
            identified_ingredients = processor.identify_food_ingredients(
                cleaned_easyocr_text
            )
            all_ingredients.extend(identified_ingredients)

            if not identified_ingredients:
                print(f"No ingredients detected from text in {image_path}. Performing image classification...")
                predicted_label, confidence = processor.classify_image(resized_image)
                if confidence > 0.5 and predicted_label.lower() != "unknown":
                    all_ingredients.append(predicted_label.lower())
        
        except Exception as e:
            print(f"Error processing image {image_path}: {str(e)}")
            continue
        finally:
            # Clean up temporary files
            try:
                if os.path.exists(image_path) and image_path.startswith('temp_'):
                    os.remove(image_path)
            except Exception as e:
                print(f"Error cleaning up temporary file {image_path}: {str(e)}")

    # Remove duplicates and sort
    unique_ingredients = list(set(all_ingredients))
    unique_ingredients.sort()
    
    return ", ".join([ing for ing in unique_ingredients if ing not in ["none", "unknown"]])

if __name__ == "__main__":
    image_paths = [r"C:\Users\amrut\Smart-Recipe-Generator_oct_2024\beetroot.jpg"]  # Example usage
    ingredients = process_uploaded_images(image_paths)
    print("Extracted Ingredients:", ingredients)
