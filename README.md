## Setup

### Backend
```
# Navigate to the backend directory
cd backend

# Create and activate a new Conda environment
conda create --name piano-uploader-env python=3.10
conda activate piano-uploader-env

# Install the required Python packages
pip install -r requirements.txt
```

### Frontend
```
cd ..
# Navigate to the frontend directory
cd frontend

# Install the required Node.js packages
npm install
```

## Running

In two separate terminals:
First:

```
cd ..
# Navigate to the backend directory
cd backend

# Activate the Conda environment
conda activate piano-uploader-env

# Run the Flask server
python app.py
```


Second:
```
# Navigate to the frontend directory
cd frontend

# Run the development script to launch the app
npm run dev
```
