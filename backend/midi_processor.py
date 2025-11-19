import os
import mido
import csv

def convert_midi_to_csv(midi_path):
    """
    Takes the path to a MIDI file, converts it to CSV,
    and returns the path of the newly created CSV file.
    """
    
    # Create the output CSV path based on the input MIDI path
    # e.g., 'uploads/temp_upload.mid' becomes 'uploads/temp_upload.csv'
    csv_path = os.path.splitext(midi_path)[0] + '.csv'
    
    absolute_time = 0.0

    try:
        midi_file = mido.MidiFile(midi_path)

        with open(csv_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['time', 'type', 'note', 'velocity'])

            for msg in midi_file:
                absolute_time += msg.time
                if msg.type in ['note_on', 'note_off']:
                    writer.writerow([f"{absolute_time:.3f}", msg.type, msg.note, msg.velocity])
        
        # Return the path of the file we just created
        return csv_path

    except Exception as e:
        print(f"Error during MIDI conversion: {e}")
        # Re-raise the exception so app.py knows something went wrong
        raise