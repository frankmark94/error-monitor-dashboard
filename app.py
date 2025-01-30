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
            'errorCode': int,
            'errorMessage': str,
            'timestamp': str,
            'connectionType': str,
            'connectionName': str,
            'additionalInfo': dict
        }
        
        for field, field_type in required_fields.items():
            if field not in data:
                return jsonify({"status": "error", "message": f"Missing required field: {field}"}), 400
            if not isinstance(data[field], field_type):
                return jsonify({"status": "error", "message": f"Invalid type for field {field}"}), 400

        # Validate additionalInfo structure
        required_additional_info = {
            'timestamp': str,
            'type': str,
            'consumer_id': str,
            'account_id': str,
            'customer_id': str
        }

        for field, field_type in required_additional_info.items():
            if field not in data['additionalInfo']:
                return jsonify({"status": "error", "message": f"Missing field in additionalInfo: {field}"}), 400
            if not isinstance(data['additionalInfo'][field], field_type):
                return jsonify({"status": "error", "message": f"Invalid type for additionalInfo.{field}"}), 400

        # Add received timestamp
        data['received_at'] = datetime.utcnow().isoformat()
        
        # Add severity based on error code
        error_code = int(data['errorCode'])
        if error_code >= 500:
            data['severity'] = 'critical'
        elif error_code >= 400:
            data['severity'] = 'warning'
        else:
            data['severity'] = 'info'

        # Update statistics
        error_stats['error_codes'][str(error_code)] += 1
        error_stats['connection_types'][data['connectionType']] += 1
        
        # Update hourly stats using the incoming timestamp
        hour = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:00')
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