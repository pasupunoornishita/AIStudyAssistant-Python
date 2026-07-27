from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
from dotenv import load_dotenv
import os
import traceback
import httpx

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Check API Key
api_key = os.getenv("GROQ_API_KEY")

print("GROQ API KEY FOUND:", api_key is not None)

if api_key:
    print("GROQ API KEY PREFIX:", api_key[:8])
else:
    print("ERROR: GROQ_API_KEY not found in .env file")

# Create Groq client
client = Groq(
    api_key=api_key,
    http_client=httpx.Client(verify=False)
)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return "AI Study Assistant Backend Running"

# Chat API
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No JSON data received"}), 400

        user_input = data.get("message")

        if not user_input:
            return jsonify({"error": "Message is required"}), 400

        print("User Input:", user_input)

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
            
                    "role": "user",
                    "content": user_input
                }
            ],
            temperature=0.7,
            max_tokens=500
        )

        answer = response.choices[0].message.content

        return jsonify({
            "response": answer
        })

    except Exception as e:
        traceback.print_exc()

        return jsonify({
            "error": str(e),
            "type": str(type(e))
        }), 500

# Embeddings API
@app.route("/embedding", methods=["POST"])
def embedding():
    try:
        data = request.get_json()
        text = data.get("text")

        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )

        return jsonify({
            "embedding": response.data[0].embedding
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500
        
# Audio API
@app.route("/audio", methods=["POST"])
def audio():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]

        filepath = os.path.join(
            UPLOAD_FOLDER,
            file.filename
        )

        file.save(filepath)

        with open(filepath, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                file=audio_file,
                model="whisper-large-v3"
            )

        return jsonify({
            "text": transcription.text
        })

    except Exception as e:
        traceback.print_exc()

        return jsonify({
            "error": str(e),
            "type": str(type(e))
        }), 500
        
# Moderation API
@app.route("/moderation", methods=["POST"])
def moderation():
    try:
        data = request.get_json()
        text = data.get("text")

        return jsonify({
            "message": "Moderation endpoint ready",
            "text": text
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

if __name__ == "__main__":
    app.run(debug=True)