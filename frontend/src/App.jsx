import { useState } from 'react'
import './App.css'

function App() {
  const [status, setStatus] = useState('Idle');
  const [isUploading, setIsUploading] = useState(false);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setIsUploading(true);
    setStatus('Uploading & Converting...');

    const formData = new FormData();
    formData.append('file', file);

    try {
      // Talk to our Python Backend
      const response = await fetch('http://localhost:5000/upload', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        setStatus(`Success: ${data.message}`);
      } else {
        setStatus(`Error: ${data.error}`);
      }
    } catch (error) {
      setStatus(`Connection Failed: Is the Python backend running?`);
      console.error(error);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="container">
      <h1>MIDI Upload</h1>
      
      <div className="card">
        <p>Select a MIDI file to send to the piano.</p>
        
        <input 
          type="file" 
          accept=".mid,.midi" 
          onChange={handleFileUpload} 
          disabled={isUploading}
        />
      </div>

      <div className={`status ${isUploading ? 'pulsing' : ''}`}>
        <strong>Status:</strong> {status}
      </div>
    </div>
  )
}

export default App