# app.py
from flask import Flask, request, jsonify, g
from flask_cors import CORS
from functools import wraps
import playwright
import os
import jwt
import time
from collections import defaultdict
import threading

app = Flask(__name__)
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', '*')
CORS(app, resources={r"/*": {"origins": [o.strip() for o in ALLOWED_ORIGINS.split(',') if o.strip()] or "*"}}, supports_credentials=False)

# Environment variables
API_SECRET_KEY = os.getenv('API_SECRET_KEY')  # For JWT
INDUSTRIOUS_USERNAME = os.getenv('INDUSTRIOUS_USERNAME')
INDUSTRIOUS_PASSWORD = os.getenv('INDUSTRIOUS_PASSWORD')
ALLOWED_API_KEYS = os.getenv('ALLOWED_API_KEYS', '').split(',')

# Rate limiting storage
request_counts = defaultdict(list)
rate_limit_lock = threading.Lock()

# Rate limiting decorator
def rate_limit(max_requests=10, window_minutes=60):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_id = get_client_identifier()
            now = time.time()
            window_start = now - (window_minutes * 60)
            
            with rate_limit_lock:
                # Clean old requests
                request_counts[client_id] = [
                    req_time for req_time in request_counts[client_id] 
                    if req_time > window_start
                ]
                
                # Check rate limit
                if len(request_counts[client_id]) >= max_requests:
                    return jsonify({
                        "success": False,
                        "error": "Rate limit exceeded. Try again later."
                    }), 429
                
                # Add current request
                request_counts[client_id].append(now)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Authentication decorator
def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({"error": "Missing Authorization header"}), 401
            
        try:
            # Support both API key and JWT
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                
                # Try JWT first
                try:
                    payload = jwt.decode(token, API_SECRET_KEY, algorithms=['HS256'])
                    g.user = payload
                except jwt.InvalidTokenError:
                    # Fall back to API key
                    if token not in ALLOWED_API_KEYS:
                        return jsonify({"error": "Invalid API key"}), 401
                    g.user = {"api_key": token}
            else:
                return jsonify({"error": "Invalid Authorization format"}), 401
                
        except Exception as e:
            return jsonify({"error": "Authentication failed"}), 401
            
        return f(*args, **kwargs)
    return decorated_function

def get_client_identifier():
    # Use JWT user ID if available, otherwise use API key or IP
    if hasattr(g, 'user'):
        return g.user.get('user_id', g.user.get('api_key', request.remote_addr))
    return request.remote_addr

@app.route('/book-room', methods=['POST'])
@require_auth
@rate_limit(max_requests=5, window_minutes=60)  # 5 bookings per hour
def book_room():
    data = request.json
    
    # Validate required fields
    required_fields = ['date', 'time', 'duration']
    for field in required_fields:
        if field not in data:
            return jsonify({
                "success": False,
                "error": f"Missing required field: {field}"
            }), 400
    
    try:
        result = automate_booking(
            data['date'], 
            data['time'], 
            data['duration'], 
            data.get('attendees', 1)
        )
        
        return jsonify({
            "success": True,
            "message": f"✅ Booked {result['room_name']} on {result['date']} from {result['time']}",
            "room_details": result
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"❌ Booking failed: {str(e)}"
        }), 500

def automate_booking(date, time, duration, attendees):
    # Use environment variables for credentials
    username = INDUSTRIOUS_USERNAME
    password = INDUSTRIOUS_PASSWORD
    
    if not username or not password:
        raise Exception("Industrious credentials not configured")
    
    # Your automation code here using the credentials
    # Return mock data for now
    return {
        "room_name": "Conference Room A",
        "date": date,
        "time": time,
        "capacity": attendees
    }

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "timestamp": time.time()})

# Simple chat endpoint for conversational responses
@app.route('/chat', methods=['POST'])
@require_auth
@rate_limit(max_requests=60, window_minutes=60)  # basic protection
def chat():
    try:
        data = request.get_json(silent=True) or {}
        message = (data.get('message') or '').strip()
        agent_id = data.get('agentId') or 'default'
        conversation_id = data.get('conversationId') or str(int(time.time()))

        if not message:
            return jsonify({
                "success": False,
                "error": "Missing 'message'"
            }), 400

        # For now, return a deterministic, safe echo to validate connectivity.
        reply = f"You said: {message}"

        return jsonify({
            "success": True,
            "response": reply,
            "agentId": agent_id,
            "conversationId": conversation_id
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Chat processing failed"
        }), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)