# app.py
from flask import Flask, request, jsonify, g
from flask_cors import CORS
from functools import wraps
import playwright
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import os
import jwt
import time
from collections import defaultdict
import threading
from openai import OpenAI

app = Flask(__name__)
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', '*')
CORS(app, resources={r"/*": {"origins": [o.strip() for o in ALLOWED_ORIGINS.split(',') if o.strip()] or "*"}}, supports_credentials=False)

# Environment variables
API_SECRET_KEY = os.getenv('API_SECRET_KEY')  # For JWT
INDUSTRIOUS_USERNAME = os.getenv('INDUSTRIOUS_USERNAME')
INDUSTRIOUS_PASSWORD = os.getenv('INDUSTRIOUS_PASSWORD')
ALLOWED_API_KEYS = os.getenv('ALLOWED_API_KEYS', '').split(',')
DEBUG_ERRORS = os.getenv('DEBUG_ERRORS', '0')
PLAYWRIGHT_HEADLESS = os.getenv('PLAYWRIGHT_HEADLESS', '1')
INDUSTRIOUS_LOGIN_URL = os.getenv('INDUSTRIOUS_LOGIN_URL', 'https://members.industriousoffice.com')
INDUSTRIOUS_BOOKING_URL = os.getenv('INDUSTRIOUS_BOOKING_URL', 'https://portal.industriousoffice.com/home/calendar/roombooking')

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
    """Automate booking flow using Playwright.

    Note: This implementation performs a login and sets the stage for booking. Since
    selectors differ across tenants, you may need to tune the selectors below to
    match the Industrious portal UI for your account.
    """
    username = INDUSTRIOUS_USERNAME
    password = INDUSTRIOUS_PASSWORD

    if not username or not password:
        raise Exception("Industrious credentials not configured")

    headless = PLAYWRIGHT_HEADLESS != '0'

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless, args=["--no-sandbox", "--disable-dev-shm-usage"])
        context = browser.new_context()
        page = context.new_page()

        try:
            # Start at booking URL; if unauthenticated the site should redirect to login
            page.goto(INDUSTRIOUS_BOOKING_URL, timeout=120_000)
            if "login" in page.url or "signin" in page.url or page.url.startswith(INDUSTRIOUS_LOGIN_URL):
                page.goto(INDUSTRIOUS_LOGIN_URL, timeout=120_000)
            # Try a few common selectors for email/password/sign in
            filled = False
            try:
                page.get_by_label("Email").fill(username)
                filled = True
            except Exception:
                pass
            if not filled:
                try:
                    page.fill('input[name="email"]', username)
                    filled = True
                except Exception:
                    pass
            if not filled:
                page.fill('input[type="email"]', username)

            filled_pw = False
            try:
                page.get_by_label("Password").fill(password)
                filled_pw = True
            except Exception:
                pass
            if not filled_pw:
                try:
                    page.fill('input[name="password"]', password)
                    filled_pw = True
                except Exception:
                    pass
            if not filled_pw:
                page.fill('input[type="password"]', password)

            # Click a button that likely logs in
            clicked = False
            for selector in [
                'button:has-text("Sign in")',
                'button:has-text("Log in")',
                'button[type="submit"]',
                'text=Sign in',
                'text=Log in',
            ]:
                try:
                    page.click(selector, timeout=5_000)
                    clicked = True
                    break
                except Exception:
                    continue

            if not clicked:
                # Press Enter as a last resort
                page.keyboard.press('Enter')

            page.wait_for_load_state('networkidle', timeout=60_000)

            # Navigate to booking page after login
            page.goto(INDUSTRIOUS_BOOKING_URL, timeout=120_000)
            page.wait_for_load_state('networkidle', timeout=60_000)

            # Heuristic: pick the room select with option '2-L' and select it
            select_count = page.locator('select').count()
            selected_room = False
            for i in range(select_count):
                sel = page.locator('select').nth(i)
                try:
                    options = [t.strip() for t in sel.locator('option').all_text_contents()]
                    match = next((o for o in options if o.lower().replace(' ', '') in ['2-l','2l','2–l']), None)
                    if match:
                        sel.select_option(label=match)
                        selected_room = True
                        break
                except Exception:
                    continue

            # Compute end time
            def _to_label(hhmm: str) -> str:
                # '15:00' -> '3:00pm'
                hh, mm = [int(x) for x in hhmm.split(':')]
                suffix = 'am' if hh < 12 else 'pm'
                h12 = hh % 12
                if h12 == 0:
                    h12 = 12
                return f"{h12}:{mm:02d}{suffix}"

            start_label = _to_label(time)
            end_minutes = int(duration)
            hh, mm = [int(x) for x in time.split(':')]
            mm_total = hh * 60 + mm + end_minutes
            end_h = (mm_total // 60) % 24
            end_m = mm_total % 60
            end_label = _to_label(f"{end_h:02d}:{end_m:02d}")

            # Heuristic: find two time selects that contain am/pm options
            time_selects = []
            for i in range(select_count):
                sel = page.locator('select').nth(i)
                try:
                    options = ' '.join(sel.locator('option').all_text_contents()).lower()
                    if 'am' in options or 'pm' in options:
                        time_selects.append(sel)
                except Exception:
                    pass
            if len(time_selects) >= 2:
                try:
                    time_selects[0].select_option(label=start_label)
                except Exception:
                    pass
                try:
                    time_selects[1].select_option(label=end_label)
                except Exception:
                    pass

            # Click a likely submit button
            for selector in [
                'button:has-text("Book")',
                'button:has-text("Reserve")',
                'text=Book',
                'text=Reserve',
            ]:
                try:
                    page.click(selector, timeout=5_000)
                    break
                except Exception:
                    continue

            page.wait_for_load_state('networkidle', timeout=30_000)

            room_name = '2-L' if selected_room else 'Selected Room'
            return {
                "room_name": room_name,
                "date": date,
                "time": f"{start_label} - {end_label}",
                "capacity": attendees,
            }
        except PlaywrightTimeoutError:
            raise Exception("Booking portal timeout during navigation or login")
        finally:
            try:
                context.close()
                browser.close()
            except Exception:
                pass

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

        # Use OpenAI for a basic chat completion
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if not openai_api_key:
            app.logger.warning("/chat called without OPENAI_API_KEY; responding with echo fallback")
            # Fallback to echo if no key configured
            reply = f"You said: {message}"
            return jsonify({
                "success": True,
                "response": reply,
                "agentId": agent_id,
                "conversationId": conversation_id
            })

        client = OpenAI(api_key=openai_api_key)
        system_prompt = "You are a concise and helpful assistant for booking and general questions."
        model_name = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')

        reply = ""
        # Primary: Chat Completions with optional tool-call to book a room
        completion = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message},
            ],
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "book_room",
                        "description": "Book a meeting room using the Industrious portal.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "date": {"type": "string", "description": "YYYY-MM-DD"},
                                "time": {"type": "string", "description": "HH:MM 24h"},
                                "duration": {"type": "integer", "description": "Duration in minutes"},
                                "attendees": {"type": "integer", "description": "Number of attendees", "default": 1}
                            },
                            "required": ["date", "time", "duration"]
                        }
                    }
                }
            ],
            temperature=0.3,
            max_tokens=400,
        )
        if completion and completion.choices and completion.choices[0].message:
            msg = completion.choices[0].message
            tool_calls = getattr(msg, "tool_calls", None)
            if tool_calls:
                try:
                    import json as _json
                    for tool_call in tool_calls:
                        fn = getattr(tool_call, "function", None)
                        if fn and fn.name == "book_room":
                            args = _json.loads(fn.arguments or "{}")
                            date = args.get("date")
                            time_str = args.get("time")
                            duration = int(args.get("duration")) if args.get("duration") is not None else None
                            attendees = int(args.get("attendees") or 1)
                            if date and time_str and duration:
                                result = automate_booking(date, time_str, duration, attendees)
                                reply = f"✅ Booked {result['room_name']} on {result['date']} from {result['time']}"
                                return jsonify({
                                    "success": True,
                                    "response": reply,
                                    "agentId": agent_id,
                                    "conversationId": conversation_id
                                })
                except Exception:
                    app.logger.exception("Tool execution failed")
            reply = (getattr(msg, "content", None) or "").strip()

        # Fallback: Responses API (some orgs route o-models here)
        if not reply:
            resp = client.responses.create(
                model=model_name,
                input=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message},
                ],
            )
            try:
                # SDK provides output_text convenience for plain text
                reply = (getattr(resp, "output_text", None) or "").strip()
            except Exception:
                reply = reply or ""

        if not reply:
            reply = "I’m here and connected, but I couldn’t generate a response just now. Please try again."

        return jsonify({
            "success": True,
            "response": reply,
            "agentId": agent_id,
            "conversationId": conversation_id
        })
    except Exception as e:
        # Log full stack to Render logs
        try:
            app.logger.exception("Chat processing failed")
        except Exception:
            pass

        error_body = {"success": False, "error": "Chat processing failed"}
        if DEBUG_ERRORS == '1':
            error_body["detail"] = str(e)
        return jsonify(error_body), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)