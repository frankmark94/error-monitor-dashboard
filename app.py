from flask import Flask, request, render_template, jsonify, send_from_directory
from datetime import datetime
import json
from collections import defaultdict
import os
from config import config

app = Flask(__name__, static_url_path='/static')
app.config.from_object(config)

# Store webhooks in memory (in production, you'd want to use a database)
webhook_logs = []
error_stats = {
    'error_codes': defaultdict(int),
    'connection_types': defaultdict(int),
    'hourly_errors': defaultdict(int)
}

@app.route('/')
def home():
    app.logger.debug('Serving index.html')
    return render_template('index.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    app.logger.debug(f'Serving static file: {filename}')
    return send_from_directory('static', filename)

@app.route(config.ENDPOINT_PATH, methods=['POST'])
def webhook_endpoint():
    try:
        data = request.json
        
        # Validate required fields
        required_fields = {
            'ErrorCode': int,
            'ErrorMessage': str,
            'Timestamp': str,
            'ConnectionType': str,
            'ConnectionName': str
        }
        
        for field, field_type in required_fields.items():
            if field not in data:
                return jsonify({"status": "error", "message": f"Missing required field: {field}"}), 400
            if not isinstance(data[field], field_type):
                return jsonify({"status": "error", "message": f"Invalid type for field {field}"}), 400

        # Add received timestamp and process the original timestamp
        data['received_at'] = datetime.utcnow().isoformat()
        
        # Add severity based on error code
        error_code = int(data['ErrorCode'])
        if error_code >= 500:
            data['severity'] = 'critical'
        elif error_code >= 400:
            data['severity'] = 'warning'
        else:
            data['severity'] = 'info'

        # Update statistics
        error_stats['error_codes'][str(error_code)] += 1
        error_stats['connection_types'][data['ConnectionType']] += 1
        
        # Update hourly stats
        hour = datetime.fromisoformat(data['Timestamp']).strftime('%Y-%m-%d %H:00')
        error_stats['hourly_errors'][hour] += 1

        webhook_logs.insert(0, data)
        if len(webhook_logs) > config.MAX_LOGS:
            webhook_logs.pop()
            
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/logs')
def get_logs():
    return jsonify(webhook_logs)

@app.route('/stats')
def get_stats():
    return jsonify(error_stats)

@app.route('/config')
def get_config():
    return jsonify({
        'ENDPOINT_PATH': config.ENDPOINT_PATH
    })

if __name__ == '__main__':
    app.logger.setLevel('DEBUG' if config.DEBUG else 'INFO')
    app.run(
        debug=config.DEBUG,
        host=config.HOST,
        port=config.PORT
    ) 