from backend.qibot import get_response
from backend.voice_input import listen_for_command
from backend.voice_output import speak_response
from backend.vault_reader import search_vault
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/qinnie/say', methods=['POST'])
def qinnie_say():
    data = request.json
    prompt = data.get('prompt')
    if not prompt:
        return jsonify({"error": "No prompt received"}), 400

    context = search_vault(prompt)
    reply = get_response(prompt, context)
    speak_response(reply)
    return jsonify({"response": reply})

if __name__ == '__main__':
    app.run(port=6543)
