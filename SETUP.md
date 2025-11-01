# Smart Crop Project - Setup Guide

## Architecture Overview

This project implements a full-stack agriculture management platform with:

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Flask (Python)
- **Database**: SQLite
- **Features**: Image Analysis, OCR, AI Chatbot, Multi-language Support

## Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Tesseract OCR (for OCR functionality)

**macOS:**
```bash
brew install tesseract
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install tesseract-ocr
```

**Windows:**
Download and install from: https://github.com/UB-Mannheim/tesseract/wiki

### 3. Initialize Database

The database will be created automatically on first run in the `instance/` folder.

### 4. Create Upload Directories

The app will create these automatically, but you can create them manually:
```bash
mkdir -p static/uploads/images
mkdir -p static/uploads/soil-reports
```

## Running the Application

```bash
python app.py
```

The application will run on `http://127.0.0.1:3001`

## API Endpoints

### Authentication
- `POST /api/login` - User login
- `POST /api/register` - User registration
- `POST /api/logout` - User logout

### Dashboard Data
- `GET /api/user-details` - Get current user information
- `GET /api/drone-images` - Get all uploaded field images
- `GET /api/soil-reports` - Get all soil reports
- `GET /api/weather-suggestion` - Get today's weather advisory

### Image Analysis
- `POST /api/analyze-image` - Upload and analyze field/drone image
  - Form data with `file` field
  - Returns: crop stress level, pest detection, nutrient deficiency

### Soil Health Advisory
- `POST /api/analyze-soil` - Upload and analyze soil report
  - Form data with `file` field (image or PDF)
  - Returns: OCR text, AI analysis, translations in English, Hindi, Marathi

### Chatbot
- `POST /api/chat` - Chat with AI assistant
  - JSON: `{"message": "your question"}`
  - Returns: AI-generated response
- `GET /api/chat-history` - Get chat history

### Profile
- `POST /api/update-profile` - Update user profile
  - JSON: `{"farmer_name", "farm_location", "crop_type", "soil_type"}`

## Integrating ML Models

### For Image Analysis:
1. Load your `pest_detector.h5` or `soil_model.pth` in `utils.py`
2. Update the `analyze_image_with_ml()` function to use your actual models
3. Preprocess images according to your model's requirements

### For AI Chatbot (Gemma):
1. Update `chat_with_gemma()` in `utils.py` with your Gemma API endpoint
2. Configure API keys and authentication
3. Adjust prompts for better context-aware responses

## Configuration

### Secret Key
Update the `SECRET_KEY` in `app.py` for production:
```python
app.config['SECRET_KEY'] = 'your-production-secret-key'
```

### Database
Change SQLite path or switch to PostgreSQL/MySQL by updating:
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/database.db'
```

## Features Implemented

✅ User authentication (login/register)  
✅ Dashboard with personalized welcome  
✅ Weather-based farming suggestions (with translations)  
✅ Field image upload and analysis  
✅ Soil report upload with OCR and AI analysis  
✅ Multi-language support (English, Hindi, Marathi)  
✅ AI chatbot with context awareness  
✅ Responsive design for mobile devices  
✅ Database models for all data types  

## Next Steps

1. **Integrate Real ML Models**: Replace placeholder analysis with your trained models
2. **Connect Gemma API**: Update chatbot function with actual API endpoint
3. **Add Weather API**: Integrate OpenWeatherMap or similar for real weather data
4. **Enhance OCR**: Fine-tune OCR for better text extraction from soil reports
5. **Add More Features**: Crop recommendations, irrigation scheduling, etc.

## Project Structure

```
nmims-bug-bugter/
├── app.py                 # Main Flask application
├── models.py              # Database models
├── utils.py               # Utility functions (ML, OCR, translation)
├── requirements.txt       # Python dependencies
├── instance/
│   └── database.db        # SQLite database (auto-created)
├── static/
│   ├── css/
│   │   └── style.css     # All styles
│   ├── js/
│   │   ├── auth.js       # Authentication logic
│   │   └── dashboard.js  # Dashboard functionality
│   └── uploads/          # User-uploaded files
│       ├── images/
│       └── soil-reports/
└── templates/
    ├── home.html          # Landing page
    ├── login.html         # Login page
    ├── dashboard.html     # Main dashboard
    └── _layout.html       # Base template
```

## Troubleshooting

**Tesseract not found:**
- Ensure Tesseract is installed and in your PATH
- On macOS/Linux, verify with: `which tesseract`

**Database errors:**
- Delete `instance/database.db` to reset the database
- Ensure the `instance/` folder exists

**Import errors:**
- Run `pip install -r requirements.txt` again
- Check Python version (requires Python 3.8+)

**CORS errors:**
- Flask-CORS is already configured
- Check browser console for specific errors

