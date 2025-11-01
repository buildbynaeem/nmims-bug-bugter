# Utility functions for image processing, OCR, AI, and translation
import os
import cv2
import numpy as np
from PIL import Image
import pytesseract
import json
from werkzeug.utils import secure_filename
import requests

# Configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}
ALLOWED_DOCUMENT_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

def allowed_file(filename, file_type='image'):
    """Check if file extension is allowed"""
    if file_type == 'image':
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS
    else:
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_DOCUMENT_EXTENSIONS

def save_uploaded_file(file, folder='images'):
    """Save uploaded file and return the file path"""
    if file and allowed_file(file.filename, 'image'):
        filename = secure_filename(file.filename)
        # Create folder if it doesn't exist
        folder_path = os.path.join(UPLOAD_FOLDER, folder)
        os.makedirs(folder_path, exist_ok=True)
        
        # Add timestamp to avoid conflicts
        import time
        timestamp = int(time.time())
        name, ext = os.path.splitext(filename)
        filename = f"{name}_{timestamp}{ext}"
        
        file_path = os.path.join(folder_path, filename)
        file.save(file_path)
        return file_path
    return None

def analyze_image_with_ml(image_path):
    """
    Analyze drone/field image using ML models for crop stress, pests, and nutrient deficiency
    This is a placeholder - integrate with your actual ML models
    """
    try:
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            return {'error': 'Could not load image'}
        
        # Convert to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Placeholder analysis - Replace with actual ML model inference
        # Example: Using color analysis as a simple placeholder
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Simple heuristics (replace with actual ML models)
        green_mask = cv2.inRange(hsv, (40, 50, 50), (80, 255, 255))
        green_percentage = (np.sum(green_mask > 0) / green_mask.size) * 100
        
        # Determine crop stress level based on green percentage
        if green_percentage < 30:
            crop_stress_level = "High"
            nutrient_deficiency = "Possible nitrogen deficiency detected"
        elif green_percentage < 60:
            crop_stress_level = "Medium"
            nutrient_deficiency = None
        else:
            crop_stress_level = "Low"
            nutrient_deficiency = None
        
        # Simple pest detection placeholder (replace with actual pest detection model)
        # In production, use your pest_detector.h5 model here
        pest_detected = False
        pest_type = None
        
        # You can load your actual models here:
        # from tensorflow import keras
        # pest_model = keras.models.load_model('ml_models/pest_detector.h5')
        # pest_prediction = pest_model.predict(preprocessed_image)
        
        result = {
            'crop_stress_level': crop_stress_level,
            'pest_detected': pest_detected,
            'pest_type': pest_type,
            'nutrient_deficiency': nutrient_deficiency,
            'green_percentage': round(green_percentage, 2),
            'image_health_score': round((green_percentage / 100) * 100, 2)
        }
        
        return result
    except Exception as e:
        return {'error': str(e)}

def extract_text_with_ocr(image_path):
    """
    Extract text from soil report image using OCR
    """
    try:
        # Load image
        image = Image.open(image_path)
        
        # Perform OCR
        text = pytesseract.image_to_string(image, lang='eng')
        
        return text.strip()
    except Exception as e:
        return f"OCR Error: {str(e)}"

def analyze_soil_with_ai(ocr_text):
    """
    Analyze soil report text using AI/LLM (Gemma or similar)
    This is a placeholder - integrate with your actual LLM API
    """
    try:
        # Placeholder - Replace with actual LLM API call
        # Example prompt for Gemma or similar LLM
        
        prompt = f"""Analyze the following soil report text and provide:
1. A brief summary of key nutrient levels (N, P, K, pH, etc.)
2. Overall soil health assessment
3. Key recommendations for the farmer

Soil Report Text:
{ocr_text}

Please provide a clear, concise analysis:"""
        
        # In production, replace this with actual API call:
        # response = requests.post('YOUR_LLM_API_ENDPOINT', json={'prompt': prompt})
        # ai_summary = response.json()['summary']
        
        # Placeholder response
        ai_summary = f"""
        **Soil Health Analysis:**
        
        Based on the soil report provided, here is a comprehensive analysis:
        
        **Key Findings:**
        - {ocr_text[:100]}... (Extracted from soil report)
        
        **Recommendations:**
        1. Monitor nutrient levels regularly
        2. Consider soil amendment based on specific deficiencies
        3. Maintain proper pH levels for optimal crop growth
        
        Note: This is a placeholder response. Integrate with your LLM API for accurate analysis.
        """
        
        return ai_summary
    except Exception as e:
        return f"AI Analysis Error: {str(e)}"

def translate_text(text, target_language='hi'):
    """
    Translate text to Marathi (mr) or Hindi (hi)
    Using googletrans library or similar translation service
    """
    try:
        from googletrans import Translator
        
        translator = Translator()
        translation = translator.translate(text, dest=target_language)
        return translation.text
    except Exception as e:
        # Fallback: return original text if translation fails
        return f"{text} [Translation unavailable: {str(e)}]"

def get_weather_suggestion(user_location, crop_type):
    """
    Get weather-based farming suggestions
    Placeholder - integrate with actual weather API
    """
    try:
        # Placeholder - replace with actual weather API (e.g., OpenWeatherMap)
        suggestion = f"""
        **Weather Advisory for {user_location}:**
        
        Today's recommendations for {crop_type}:
        - Current conditions suggest moderate irrigation
        - Temperature is optimal for growth
        - Watch for pest activity during this season
        
        Note: Integrate with a weather API (OpenWeatherMap, WeatherAPI) for real-time data.
        """
        return suggestion
    except Exception as e:
        return f"Weather suggestion error: {str(e)}"

def chat_with_gemma(user_query, user_context=None):
    """
    Send user query to Gemma LLM API
    Enhanced with user's farm context for better responses
    """
    try:
        # Build context-aware prompt
        context_prompt = ""
        if user_context:
            context_prompt = f"""
            User Context:
            - Farm Location: {user_context.get('farm_location', 'Not specified')}
            - Crop Type: {user_context.get('crop_type', 'Not specified')}
            - Soil Type: {user_context.get('soil_type', 'Not specified')}
            
            """
        
        full_prompt = f"""{context_prompt}
        User Question: {user_query}
        
        Please provide a helpful, accurate answer based on the context above:"""
        
        # Placeholder - Replace with actual Gemma API call
        # response = requests.post('YOUR_GEMMA_API_ENDPOINT', json={
        #     'prompt': full_prompt,
        #     'max_tokens': 500
        # })
        # return response.json()['response']
        
        # Placeholder response
        response = f"""
        **Answer to: "{user_query}"**
        
        Based on your farm context ({user_context.get('crop_type', 'farming') if user_context else 'general farming'}), 
        here is my recommendation:
        
        This is a placeholder response. Please integrate with the Gemma API for accurate, context-aware answers.
        You can enhance this by:
        1. Connecting to Gemma API endpoint
        2. Including user's farm data in the prompt
        3. Handling conversation history for better context
        """
        
        return response.strip()
    except Exception as e:
        return f"Chat error: {str(e)}"

