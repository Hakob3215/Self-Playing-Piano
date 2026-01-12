from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import serial
import time
from midi_processor import convert_midi_to_csv

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
CURRENT_SONG_FILENAME = 'current.csv'
CURRENT_SONG_PATH = os.path.join(UPLOAD_FOLDER, CURRENT_SONG_FILENAME)

# Serial Configuration - UPDATE THIS TO MATCH YOUR ESP DEVICE
SERIAL_PORT = 'COM9'  # Windows example 'COM3', Linux/Mac '/dev/ttyUSB0'
BAUD_RATE = 115200

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def send_csv_to_esp(csv_path):
    """
    Reads the CSV file and sends it line-by-line to the ESP via Serial.
    """
    if not os.path.exists(csv_path):
        print("File not found.")
        return False

    try:
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
            print(f"Connected to {SERIAL_PORT}")
            
            # Give the connection a moment to settle
            time.sleep(2)
            
            # Send Start Signal
            ser.write(b"START_UPLOAD\n")
            print("Sent START_UPLOAD")
            time.sleep(0.1) # small delay

            # Send File Content
            with open(csv_path, 'r') as f:
                for line in f:
                    ser.write(line.encode('utf-8'))
                    
                    # Wait for ACK from ESP
                    # This prevents buffer overflow on the ESP side
                    start_time = time.time()
                    ack_received = False
                    while (time.time() - start_time) < 1.0: # 1 second timeout per line
                        if ser.in_waiting > 0:
                            response = ser.readline().decode('utf-8').strip()
                            if response == "OK":
                                ack_received = True
                                break
                    
                    if not ack_received:
                        print(f"Warning: No ACK received for line: {line.strip()}")
            
            # Send End Signal
            ser.write(b"\nEND_UPLOAD\n") # Ensure newline before END
            print("Sent END_UPLOAD")
            return True

    except Exception as e:
        print(f"Serial Error: {e}")
        return False

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

    # 4. Trigger Serial Upload to ESP
    try:
        success = send_csv_to_esp(CURRENT_SONG_PATH)
        if success:
            return jsonify({'message': 'File processed and sent to Piano!'})
        else:
            return jsonify({'message': 'File processed, but failed to send to Piano (Serial Error). Check connection.'})
    except Exception as e:
        return jsonify({'message': f'File processed, but Serial error occurred: {str(e)}'})

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