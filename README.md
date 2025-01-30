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
    "errorCode": 404,
    "errorMessage": "Request failed with status code 404",
    "timestamp": "2024-01-30T19:42:10.939Z",
    "connectionType": "chat",
    "connectionName": "chat_09c5aff3-b653-4301-9780-fdb3dbfbdb42",
    "additionalInfo": {
        "timestamp": "2024-01-30T19:42:10.939Z",
        "type": "typing_indicator",
        "consumer_id": "52a390ee-e7a7-42c9-b725-b62b70c8ac2f",
        "account_id": "chat_09c5aff3-b653-4301-9780-fdb3dbfbdb42",
        "customer_id": "65e903e8f4d840cc90958e50fe1638be"
    }
}
```

The dashboard will:
- Display the error in the data table
- Show additional info in an expandable row
- Update error statistics and charts
- Color-code the severity based on the error code:
  - 500+: Critical (Red)
  - 400-499: Warning (Yellow)
  - Others: Info (Blue)

## License

MIT License 