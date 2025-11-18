import os
import mido
import csv

def convert_midi_to_csv(midi_path):
    """
    Converts MIDI to CSV using mido.
    Returns the path to the generated CSV file.
    """
    print(f"Converting {midi_path} to CSV...")
    
    # Generate output filename (replace extension with .csv)
    csv_path = os.path.splitext(midi_path)[0] + '.csv'
    
    absolute_time = 0.0

    try:
        midi_file = mido.MidiFile(midi_path)
        
        with open(csv_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            # Header row
            writer.writerow(['time', 'type', 'note', 'velocity'])

            for msg in midi_file:
                absolute_time += msg.time
                if msg.type in ['note_on', 'note_off']:
                    writer.writerow([f"{absolute_time:.3f}", msg.type, msg.note, msg.velocity])

        return csv_path
    
    except Exception as e:
        print(f"Error converting MIDI: {e}")
        raise e