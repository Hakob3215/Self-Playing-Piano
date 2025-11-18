from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from queue_manager import QueueManager
from serial_controller import SerialController
from midi_processor import convert_midi_to_csv

app = Flask(__name__)
CORS(app) # Allow React UI to talk to this

# Initialize our helpers
queue_mgr = QueueManager()
serial_ctrl = SerialController(port='COM3') # UPDATE THIS PORT!
serial_ctrl.connect()

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def play_next():
    """Callback function: triggers when a song finishes"""
    next_song = queue_mgr.get_next_song()
    if next_song:
        serial_ctrl.send_song(next_song, on_finish_callback=play_next)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # 1. Save MIDI
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    
    # 2. Convert to CSV
    csv_path = convert_midi_to_csv(filepath)
    
    # 3. Add to Queue
    queue_mgr.add_song(csv_path)
    
    # 4. If nothing is playing, start immediately
    if not serial_ctrl.is_playing:
        play_next()

    return jsonify({'message': 'File uploaded and queued', 'queue': queue_mgr.get_queue_list()})

@app.route('/queue', methods=['GET'])
def get_queue():
    return jsonify({
        'current': queue_mgr.current_song,
        'queue': queue_mgr.get_queue_list()
    })

if __name__ == '__main__':
    app.run(port=5000, debug=True)