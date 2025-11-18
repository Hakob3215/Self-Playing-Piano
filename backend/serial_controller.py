import serial
import time
import threading

class SerialController:
    def __init__(self, port='COM3', baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        self.is_playing = False

    def connect(self):
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
            print(f"Connected to {self.port}")
            return True
        except Exception as e:
            print(f"Failed to connect: {e}")
            return False

    def send_song(self, csv_path, on_finish_callback):
        """
        Reads CSV and sends it line by line.
        Runs in a separate thread to not block the server.
        """
        if not self.ser:
            print("Serial not connected")
            return

        self.is_playing = True
        
        def play_thread():
            print(f"Starting playback for {csv_path}")
            with open(csv_path, 'r') as f:
                for line in f:
                    if not self.is_playing: break # Allow stopping
                    
                    # Send line to ESP
                    self.ser.write(line.encode('utf-8'))
                    
                    # Wait for ESP to say it's ready for next line (Handshake)
                    # This is crucial! Adjust based on your ESP code.
                    # response = self.ser.readline() 
                    
                    time.sleep(0.05) # Artificial delay if no handshake
            
            self.is_playing = False
            print("Song finished")
            if on_finish_callback:
                on_finish_callback()

        threading.Thread(target=play_thread).start()