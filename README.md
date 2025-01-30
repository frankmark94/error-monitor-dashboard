# Error Monitor Dashboard

A real-time error monitoring dashboard that displays errors and statistics from various digital messaging systems. Built with Flask and Chart.js.

## Features

- Real-time error monitoring
- Configurable webhook endpoint
- Error statistics and visualizations
- Severity-based error classification
- Interactive data table with filtering and sorting
- Beautiful, responsive UI

## Local Development

1. Clone the repository:
```bash
git clone https://github.com/frankmark94/error-monitor-dashboard.git
cd error-monitor-dashboard
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Create a `.env` file:
```bash
FLASK_DEBUG=True
SECRET_KEY=your-secret-key
ENDPOINT_PATH=/endpoint
MAX_LOGS=100
HOST=0.0.0.0
PORT=5000
```

4. Run the development server:
```bash
python app.py
```

## Deployment to Render.com

1. Fork or clone this repository to your GitHub account

2. Create a new Web Service on Render.com:
   - Connect your GitHub repository
   - Select the Python environment
   - The build command will be: `pip install -r requirements.txt`
   - The start command will be: `gunicorn app:app`

3. Set up environment variables in Render.com dashboard:
   - `SECRET_KEY`: Generate a secure random key
   - `FLASK_DEBUG`: Set to `False`
   - `ENDPOINT_PATH`: Set to desired webhook path (default: `/endpoint`)
   - `MAX_LOGS`: Set maximum number of logs to keep (default: `100`)

4. Deploy the service

## Testing the Webhook

Send a POST request to your webhook endpoint with the following JSON structure:

```json
{
    "ErrorCode": 500,
    "ErrorMessage": "Internal Server Error",
    "Timestamp": "2024-01-30T20:00:00",
    "ConnectionType": "REST",
    "ConnectionName": "UserService"
}
```

## License

MIT License 