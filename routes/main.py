from flask import Blueprint, render_template, request, jsonify, session
import uuid

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Main landing page"""
    return render_template('index.html')

@main_bp.route('/chat')
def chat():
    """Chat interface page"""
    # Generate session ID if not exists
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    
    return render_template('chat.html', session_id=session['session_id'])

@main_bp.route('/health')
def health():
    """Simple health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Multi-Agent Assistant"
    })
