#!/usr/bin/env python3
"""
Intelligence OS Platform - Backend API
Fast deployment version with core functionality
"""

import os
import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import redis
import json

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://intelligence_user:intelligence_pass@postgres:5432/intelligence_os')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['REDIS_URL'] = os.getenv('REDIS_URL', 'redis://redis:6379')

# Initialize extensions
CORS(app)
db = SQLAlchemy(app)

# Initialize Redis
try:
    redis_client = redis.from_url(app.config['REDIS_URL'])
    redis_client.ping()
    print("✓ Redis connection established")
except Exception as e:
    print(f"⚠ Redis connection failed: {e}")
    redis_client = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple database models
class Meeting(db.Model):
    __tablename__ = 'meetings'
    
    id = db.Column(db.String(36), primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    date_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), default='scheduled')
    participants = db.Column(db.JSON, default=list)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Transcript(db.Model):
    __tablename__ = 'transcripts'
    
    id = db.Column(db.String(36), primary_key=True)
    meeting_id = db.Column(db.String(36), db.ForeignKey('meetings.id'))
    content = db.Column(db.Text)
    processed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# API Routes
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        db.session.execute(db.text('SELECT 1'))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    # Check Redis connection
    redis_status = "healthy" if redis_client else "unavailable"
    
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "services": {
            "database": db_status,
            "redis": redis_status
        }
    })

@app.route('/api/meetings', methods=['GET', 'POST'])
def meetings():
    """Meetings endpoint"""
    if request.method == 'GET':
        try:
            meetings = Meeting.query.all()
            return jsonify({
                "meetings": [{
                    "id": m.id,
                    "title": m.title,
                    "date_time": m.date_time.isoformat() if m.date_time else None,
                    "status": m.status,
                    "participants": m.participants or []
                } for m in meetings]
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            meeting = Meeting(
                id=data.get('id', str(datetime.utcnow().timestamp())),
                title=data.get('title', 'Untitled Meeting'),
                date_time=datetime.fromisoformat(data.get('date_time', datetime.utcnow().isoformat())),
                status=data.get('status', 'scheduled'),
                participants=data.get('participants', [])
            )
            db.session.add(meeting)
            db.session.commit()
            
            return jsonify({
                "message": "Meeting created successfully",
                "meeting_id": meeting.id
            }), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@app.route('/api/transcripts', methods=['POST'])
def upload_transcript():
    """Upload meeting transcript for processing"""
    try:
        data = request.get_json()
        transcript = Transcript(
            id=str(datetime.utcnow().timestamp()),
            meeting_id=data.get('meeting_id'),
            content=data.get('content', ''),
            processed=False
        )
        db.session.add(transcript)
        db.session.commit()
        
        # Queue for processing (simplified)
        if redis_client:
            redis_client.lpush('transcript_queue', json.dumps({
                'transcript_id': transcript.id,
                'meeting_id': transcript.meeting_id,
                'content': transcript.content
            }))
        
        return jsonify({
            "message": "Transcript uploaded successfully",
            "transcript_id": transcript.id,
            "queued_for_processing": redis_client is not None
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/analysis/<transcript_id>', methods=['GET'])
def get_analysis(transcript_id):
    """Get analysis results for a transcript"""
    try:
        # Simplified analysis response
        analysis = {
            "transcript_id": transcript_id,
            "status": "completed",
            "oracle_protocol_version": "9.1",
            "analysis": {
                "executive_summary": {
                    "key_decisions": ["Decision 1", "Decision 2"],
                    "action_items": ["Action 1", "Action 2"],
                    "strategic_implications": ["Implication 1", "Implication 2"]
                },
                "human_needs_analysis": {
                    "certainty": 7,
                    "variety": 6,
                    "significance": 8,
                    "connection": 7,
                    "growth": 6,
                    "contribution": 8
                },
                "strategic_alignment": {
                    "sdg_alignment": 0.75,
                    "doughnut_economy": 0.68,
                    "agreement_economy": 0.82
                }
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
        return jsonify(analysis)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/voice/process', methods=['POST'])
def process_voice():
    """Voice processing endpoint"""
    try:
        # Simplified voice processing response
        return jsonify({
            "status": "processed",
            "transcript": "This is a sample transcript from voice processing.",
            "confidence": 0.95,
            "speaker_identification": {
                "speakers": ["Speaker 1", "Speaker 2"],
                "segments": [
                    {"speaker": "Speaker 1", "text": "Hello, let's start the meeting.", "timestamp": 0.0},
                    {"speaker": "Speaker 2", "text": "Great, I'm ready to begin.", "timestamp": 3.5}
                ]
            },
            "processed_at": datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/dashboard/stats', methods=['GET'])
def dashboard_stats():
    """Dashboard statistics endpoint"""
    try:
        stats = {
            "total_meetings": Meeting.query.count(),
            "total_transcripts": Transcript.query.count(),
            "processed_transcripts": Transcript.query.filter_by(processed=True).count(),
            "system_status": "operational",
            "last_updated": datetime.utcnow().isoformat()
        }
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Initialize database
@app.before_first_request
def create_tables():
    """Create database tables"""
    try:
        db.create_all()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")

if __name__ == '__main__':
    # Create tables
    with app.app_context():
        db.create_all()
        logger.info("Database initialized")
    
    # Run the application
    app.run(host='0.0.0.0', port=8000, debug=True)