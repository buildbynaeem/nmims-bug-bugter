# Your main Flask application (backend logic, API routes)
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime
from models import db, User, DroneImage, SoilReport, WeatherSuggestion, ChatHistory
from utils import (
    save_uploaded_file, analyze_image_with_ml, extract_text_with_ocr,
    analyze_soil_with_ai, translate_text, get_weather_suggestion, chat_with_gemma
)

app = Flask(__name__)
CORS(app)  # Enable CORS for API calls

# Configuration
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize database
db.init_app(app)

# Create tables on first run
with app.app_context():
    db.create_all()

# ==================== Page Routes ====================

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    # Check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

# ==================== Authentication API ====================

@app.route('/api/login', methods=['POST'])
def api_login():
    """Handle user login"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'user': user.to_dict()
            }), 200
        else:
            return jsonify({'error': 'Invalid email or password'}), 401
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/register', methods=['POST'])
def api_register():
    """Handle user registration"""
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        farmer_name = data.get('farmer_name', '')
        farm_location = data.get('farm_location', '')
        
        if not username or not email or not password:
            return jsonify({'error': 'Username, email, and password required'}), 400
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        # Create new user
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            farmer_name=farmer_name,
            farm_location=farm_location
        )
        
        db.session.add(user)
        db.session.commit()
        
        session['user_id'] = user.id
        
        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/logout', methods=['POST'])
def api_logout():
    """Handle user logout"""
    session.pop('user_id', None)
    return jsonify({'success': True, 'message': 'Logged out successfully'}), 200

# ==================== Dashboard API ====================

@app.route('/api/user-details', methods=['GET'])
def api_user_details():
    """Get current user details"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(user.to_dict()), 200

@app.route('/api/drone-images', methods=['GET'])
def api_drone_images():
    """Get all drone images for current user"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    images = DroneImage.query.filter_by(user_id=session['user_id']).order_by(DroneImage.created_at.desc()).all()
    return jsonify([img.to_dict() for img in images]), 200

@app.route('/api/soil-reports', methods=['GET'])
def api_soil_reports():
    """Get all soil reports for current user"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    reports = SoilReport.query.filter_by(user_id=session['user_id']).order_by(SoilReport.created_at.desc()).all()
    return jsonify([report.to_dict() for report in reports]), 200

@app.route('/api/weather-suggestion', methods=['GET'])
def api_weather_suggestion():
    """Get today's weather-based farming suggestion"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Check if suggestion exists for today
    today = datetime.utcnow().date()
    suggestion = WeatherSuggestion.query.filter_by(
        user_id=user.id,
        date=today
    ).first()
    
    if not suggestion:
        # Generate new suggestion
        suggestion_text = get_weather_suggestion(user.farm_location or 'Unknown', user.crop_type or 'General')
        suggestion_marathi = translate_text(suggestion_text, 'mr')
        suggestion_hindi = translate_text(suggestion_text, 'hi')
        
        suggestion = WeatherSuggestion(
            user_id=user.id,
            date=today,
            suggestion_text=suggestion_text,
            suggestion_marathi=suggestion_marathi,
            suggestion_hindi=suggestion_hindi
        )
        db.session.add(suggestion)
        db.session.commit()
    
    return jsonify({
        'suggestion_text': suggestion.suggestion_text,
        'suggestion_marathi': suggestion.suggestion_marathi,
        'suggestion_hindi': suggestion.suggestion_hindi,
        'date': suggestion.date.isoformat() if suggestion.date else None
    }), 200

# ==================== Image Analysis API ====================

@app.route('/api/analyze-image', methods=['POST'])
def api_analyze_image():
    """Analyze uploaded drone/field image"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        # Save uploaded file
        file_path = save_uploaded_file(file, folder='images')
        if not file_path:
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Analyze image with ML
        analysis_result = analyze_image_with_ml(file_path)
        
        if 'error' in analysis_result:
            return jsonify({'error': analysis_result['error']}), 500
        
        # Save to database
        drone_image = DroneImage(
            user_id=session['user_id'],
            filename=secure_filename(file.filename),
            file_path=file_path,
            analysis_result=json.dumps(analysis_result),
            crop_stress_level=analysis_result.get('crop_stress_level'),
            pest_detected=analysis_result.get('pest_detected', False),
            pest_type=analysis_result.get('pest_type'),
            nutrient_deficiency=analysis_result.get('nutrient_deficiency')
        )
        
        db.session.add(drone_image)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'analysis': analysis_result,
            'image_id': drone_image.id,
            'file_path': file_path
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==================== Soil Health Advisory API ====================

@app.route('/api/analyze-soil', methods=['POST'])
def api_analyze_soil():
    """Analyze soil report with OCR, AI, and translation"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        # Save uploaded file
        file_path = save_uploaded_file(file, folder='soil-reports')
        if not file_path:
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Step 1: OCR - Extract text from image
        ocr_text = extract_text_with_ocr(file_path)
        
        # Step 2: AI Analysis - Analyze with LLM
        analysis_summary = analyze_soil_with_ai(ocr_text)
        
        # Step 3: Translation
        analysis_marathi = translate_text(analysis_summary, 'mr')
        analysis_hindi = translate_text(analysis_summary, 'hi')
        
        # Extract recommendations (simple extraction - enhance with AI)
        recommendations = "Based on the soil analysis, consider consulting with an agricultural expert for specific recommendations."
        recommendations_marathi = translate_text(recommendations, 'mr')
        recommendations_hindi = translate_text(recommendations, 'hi')
        
        # Save to database
        soil_report = SoilReport(
            user_id=session['user_id'],
            filename=secure_filename(file.filename),
            file_path=file_path,
            ocr_text=ocr_text,
            analysis_summary=analysis_summary,
            analysis_marathi=analysis_marathi,
            analysis_hindi=analysis_hindi,
            recommendations=recommendations,
            recommendations_marathi=recommendations_marathi,
            recommendations_hindi=recommendations_hindi
        )
        
        db.session.add(soil_report)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'ocr_text': ocr_text[:500],  # Return first 500 chars
            'analysis_summary': analysis_summary,
            'analysis_marathi': analysis_marathi,
            'analysis_hindi': analysis_hindi,
            'recommendations': recommendations,
            'recommendations_marathi': recommendations_marathi,
            'recommendations_hindi': recommendations_hindi,
            'report_id': soil_report.id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==================== Chatbot API ====================

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """Chat with Gemma AI chatbot"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        user_query = data.get('message', '').strip()
        
        if not user_query:
            return jsonify({'error': 'Message is required'}), 400
        
        # Get user context for better responses
        user = User.query.get(session['user_id'])
        user_context = {
            'farm_location': user.farm_location,
            'crop_type': user.crop_type,
            'soil_type': user.soil_type
        } if user else None
        
        # Get response from Gemma
        response = chat_with_gemma(user_query, user_context)
        
        # Save to chat history
        chat_history = ChatHistory(
            user_id=session['user_id'],
            message=user_query,
            response=response
        )
        db.session.add(chat_history)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'response': response
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat-history', methods=['GET'])
def api_chat_history():
    """Get chat history for current user"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    chats = ChatHistory.query.filter_by(user_id=session['user_id']).order_by(ChatHistory.created_at.desc()).limit(50).all()
    return jsonify([chat.to_dict() for chat in chats]), 200

# ==================== User Profile Update ====================

@app.route('/api/update-profile', methods=['POST'])
def api_update_profile():
    """Update user profile information"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        user = User.query.get(session['user_id'])
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Update fields
        if 'farmer_name' in data:
            user.farmer_name = data['farmer_name']
        if 'farm_location' in data:
            user.farm_location = data['farm_location']
        if 'crop_type' in data:
            user.crop_type = data['crop_type']
        if 'soil_type' in data:
            user.soil_type = data['soil_type']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Create upload directories
    os.makedirs('static/uploads/images', exist_ok=True)
    os.makedirs('static/uploads/soil-reports', exist_ok=True)
    
    app.run(debug=True, port=3001, host='127.0.0.1')
