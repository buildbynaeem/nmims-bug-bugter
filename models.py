# Database models for SQLite
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    farmer_name = db.Column(db.String(100))
    farm_location = db.Column(db.String(200))
    crop_type = db.Column(db.String(100))
    soil_type = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    drone_images = db.relationship('DroneImage', backref='user', lazy=True)
    soil_reports = db.relationship('SoilReport', backref='user', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'farmer_name': self.farmer_name,
            'farm_location': self.farm_location,
            'crop_type': self.crop_type,
            'soil_type': self.soil_type
        }

class DroneImage(db.Model):
    __tablename__ = 'drone_images'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    analysis_result = db.Column(db.Text)  # JSON string of analysis results
    crop_stress_level = db.Column(db.String(50))
    pest_detected = db.Column(db.Boolean, default=False)
    pest_type = db.Column(db.String(100))
    nutrient_deficiency = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'file_path': self.file_path,
            'analysis_result': self.analysis_result,
            'crop_stress_level': self.crop_stress_level,
            'pest_detected': self.pest_detected,
            'pest_type': self.pest_type,
            'nutrient_deficiency': self.nutrient_deficiency,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class SoilReport(db.Model):
    __tablename__ = 'soil_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    ocr_text = db.Column(db.Text)  # Raw OCR extracted text
    analysis_summary = db.Column(db.Text)  # AI-generated summary in English
    analysis_marathi = db.Column(db.Text)  # Translated to Marathi
    analysis_hindi = db.Column(db.Text)  # Translated to Hindi
    nutrient_levels = db.Column(db.Text)  # JSON string of nutrient data
    recommendations = db.Column(db.Text)  # Recommendations in English
    recommendations_marathi = db.Column(db.Text)
    recommendations_hindi = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'file_path': self.file_path,
            'analysis_summary': self.analysis_summary,
            'analysis_marathi': self.analysis_marathi,
            'analysis_hindi': self.analysis_hindi,
            'nutrient_levels': self.nutrient_levels,
            'recommendations': self.recommendations,
            'recommendations_marathi': self.recommendations_marathi,
            'recommendations_hindi': self.recommendations_hindi,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class WeatherSuggestion(db.Model):
    __tablename__ = 'weather_suggestions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, default=datetime.utcnow)
    suggestion_text = db.Column(db.Text)
    suggestion_marathi = db.Column(db.Text)
    suggestion_hindi = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ChatHistory(db.Model):
    __tablename__ = 'chat_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'message': self.message,
            'response': self.response,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

