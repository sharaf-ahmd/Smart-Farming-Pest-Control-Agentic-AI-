from flask import Flask,request,jsonify,send_from_directory
from flask_cors import CORS
import util
import os
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt
import traceback
from langchain_core.messages import HumanMessage, AIMessage
from Orchestration import app as orchestration_app

from auth import init_auth 
load_dotenv()

app=Flask(__name__)
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "super-secret-key")
jwt = JWTManager(app)
bcrypt = Bcrypt(app)
init_auth(app)  
util.load_saved_artifacts()

# Store conversation sessions for orchestration
orchestration_sessions = {} 

@app.route('/<path:filename>')
def serve_client_files(filename):
    return send_from_directory('../Client', filename)

@app.route('/')
def home():
    return send_from_directory('../Client', 'index.html')


@app.route('/pestIdentifier')
def pest_identifier():
    return send_from_directory('../Client', 'pest_detector.html')

@app.route('/detectPest', methods=['GET','POST'])
def predict_pest():

    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    
    #  Save file temporarily
    os.makedirs("uploads", exist_ok=True)
    file_path = os.path.join("uploads", file.filename)
    file.save(file_path)

    # Get predictions
    predictions = util.get_prediction(file_path)

    return jsonify(predictions)



@app.route('/impactAnalyzer')
def impactAnalyzer():
    return send_from_directory('../client', 'Impact_analyzer.html')


@app.route('/analyzeImpact', methods=['POST'])
def Analyze():
    data=request.json
    pest=data.get("pest")
    crop=data.get("crop")

    if not pest or not crop:
        return jsonify({"error": "Both 'pest' and 'crop' must be provided"}), 400
    
    result=util.analyze(pest,crop)
    return jsonify({"Impact analysis": result})
    
@app.route('/login')
def serve_login():
    return send_from_directory('static', 'login.html')

@app.route('/register')
def serve_register():
    return send_from_directory('static', 'register.html')



@app.route('/treatment')
def treatment():
    return send_from_directory('../Client', 'Treatment.html')

@app.route('/recommend', methods=['POST'])
def reccomend():
    data=request.json
    pest=data.get("pest")
    crop=data.get("crop")

    if not pest or not crop:
        return jsonify({"error": "Both 'pest' and 'crop' must be provided"}), 400
    
    result=util.reccomend(pest,crop)
    return jsonify({"Treatment Recommendations": result})

@app.route('/chatbot')
def chatbot_page():
    return send_from_directory('../Client', 'chat.html')



# Chatbot
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    chat_input = data.get("chat_input")
    session_id = data.get("session_id", "default")

    if not chat_input:
        return jsonify({"error": "chat_input is required"}), 400

    bot = util.bot

    try:
        response = bot.invoke(
            {"input": chat_input},
            config={"configurable": {"session_id": session_id}}
        )

        # Extract answer
        if isinstance(response, dict) and "answer" in response:
            response_text = response["answer"]
        else:
            response_text = str(response)

        return jsonify({"response": response_text})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "Internal server error"}), 500


# -------------------------------
# ORCHESTRATION AGENT ENDPOINTS
# -------------------------------

@app.route('/orchestration')
def orchestration_page():
    """Serve the orchestration chat page"""
    return send_from_directory('../Client', 'orchestration.html')


@app.route('/orchestrate', methods=['POST'])
def orchestrate():
    """
    Main orchestration endpoint - handles multi-step pest management workflow
    """
    try:
        data = request.json
        user_message = data.get("message")
        session_id = data.get("session_id", "default")
        image_path = data.get("image_path", None)
        
        if not user_message:
            return jsonify({"error": "message is required"}), 400
        
        # Get or create session conversation history
        if session_id not in orchestration_sessions:
            orchestration_sessions[session_id] = []
        
        messages = orchestration_sessions[session_id]
        
        # If image path provided, include it in the message
        if image_path:
            user_message = f"{user_message} Image path: {image_path}"
        
        # Add user message
        messages.append(HumanMessage(content=user_message))
        
        # Invoke orchestration agent
        state = {"messages": messages}
        result = orchestration_app.invoke(state)
        
        # Update session with new messages
        orchestration_sessions[session_id] = result["messages"]
        
        # Extract AI response and tool calls
        response_text = ""
        tools_used = []
        
        for msg in reversed(result["messages"]):
            if isinstance(msg, AIMessage):
                if msg.content:
                    response_text = msg.content
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    tools_used = [tc['name'] for tc in msg.tool_calls]
                break
        
        return jsonify({
            "response": response_text,
            "session_id": session_id,
            "tool_calls": tools_used,
            "conversation_length": len(result["messages"])
        })
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/orchestrate/upload', methods=['POST'])
def orchestrate_with_upload():
    """
    Orchestration endpoint with image upload support
    """
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        
        file = request.files['file']
        user_message = request.form.get('message', 'Can you analyze this image?')
        session_id = request.form.get('session_id', 'default')
        
        # Save file
        os.makedirs("uploads", exist_ok=True)
        file_path = os.path.join("uploads", file.filename)
        file.save(file_path)
        
        # Get or create session
        if session_id not in orchestration_sessions:
            orchestration_sessions[session_id] = []
        
        messages = orchestration_sessions[session_id]
        
        # Add user message with image path
        full_message = f"{user_message} Image path: {file_path}"
        messages.append(HumanMessage(content=full_message))
        
        # Invoke orchestration agent
        state = {"messages": messages}
        result = orchestration_app.invoke(state)
        
        # Update session
        orchestration_sessions[session_id] = result["messages"]
        
        # Extract response
        response_text = ""
        tools_used = []
        
        for msg in reversed(result["messages"]):
            if isinstance(msg, AIMessage):
                if msg.content:
                    response_text = msg.content
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    tools_used = [tc['name'] for tc in msg.tool_calls]
                break
        
        return jsonify({
            "response": response_text,
            "session_id": session_id,
            "tool_calls": tools_used,
            "image_path": file_path,
            "conversation_length": len(result["messages"])
        })
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/orchestrate/reset', methods=['POST'])
def reset_orchestration_session():
    """Reset/clear a conversation session"""
    data = request.json
    session_id = data.get("session_id", "default")
    
    if session_id in orchestration_sessions:
        del orchestration_sessions[session_id]
    
    return jsonify({
        "message": f"Session {session_id} reset successfully"
    })


@app.route('/orchestrate/sessions', methods=['GET'])
def get_orchestration_sessions():
    """Get all active session IDs"""
    return jsonify({
        "sessions": list(orchestration_sessions.keys()),
        "count": len(orchestration_sessions)
    })



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
