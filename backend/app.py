from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
from midi_processor import convert_midi_to_csv

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
CURRENT_SONG_FILENAME = 'current.csv'
CURRENT_SONG_PATH = os.path.join(UPLOAD_FOLDER, CURRENT_SONG_FILENAME)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # 1. Save the incoming MIDI temporarily
    # We use a fixed temp name so we don't fill up the disk with old files
    temp_midi_path = os.path.join(UPLOAD_FOLDER, 'temp_upload.mid')
    file.save(temp_midi_path)
    
    # 2. Convert to CSV
    # This will generate 'temp_upload.csv' in the same folder
    try:
        generated_csv_path = convert_midi_to_csv(temp_midi_path)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    # 3. Overwrite the "current" file with this new one
    if os.path.exists(CURRENT_SONG_PATH):
        os.remove(CURRENT_SONG_PATH)
    
    os.rename(generated_csv_path, CURRENT_SONG_PATH)
    
    # Clean up the temp midi file
    if os.path.exists(temp_midi_path):
        os.remove(temp_midi_path)

    return jsonify({'message': 'File updated. ESP will read this on next reset.'})

@app.route('/current.csv', methods=['GET'])
def get_current_song():
    """
    Endpoint for the ESP to fetch the file if it's using WiFi/HTTP,
    or for debugging to see what the current song is.
    """
    if os.path.exists(CURRENT_SONG_PATH):
        return send_file(CURRENT_SONG_PATH, mimetype='text/csv', as_attachment=False)
    else:
        return "No song uploaded yet", 404

if __name__ == '__main__':
    # host='0.0.0.0' allows external devices (like an ESP on the same WiFi) to connect
    app.run(port=5000, debug=True, host='0.0.0.0')