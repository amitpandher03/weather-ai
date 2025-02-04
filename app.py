from flask import Flask, request, jsonify, session, render_template
from flask_cors import CORS
from weather_ai import chat, get_weather
import os

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-key-please-change")
CORS(app)  # Enable CORS if needed

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def handle_chat():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.get_json()
    if 'message' not in data:
        return jsonify({"error": "Missing 'message' in request"}), 400
    
    # Get existing history or initialize
    session.setdefault('chat_history', [])
    
    user_message = data['message']
    bot_response = chat(user_message, session['chat_history'])
    
    # Store both messages in history
    session['chat_history'].extend([
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": bot_response}
    ])
    
    return jsonify({"response": bot_response})

@app.route('/weather', methods=['POST'])
def handle_weather():
    data = request.get_json()
    if not data or 'location' not in data:
        return jsonify({"error": "Missing required 'location' parameter"}), 400
    
    result = get_weather(
        location=data['location'],
        unit=data.get('unit', 'fahrenheit'),
        format=data.get('format', 'text')
    )
    
    return jsonify({"result": result})

if __name__ == '__main__':
    app.run(debug=True) 