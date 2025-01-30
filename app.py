from flask import Flask, request, render_template, jsonify, send_from_directory
from datetime import datetime
import json
from collections import defaultdict
import os
from config import config
import redis
from json import dumps, loads

app = Flask(__name__, static_url_path='/static')
app.config.from_object(config)

# Initialize Redis connection
redis_client = redis.from_url(config.REDIS_URL)

def get_stats():
    """Get statistics from Redis"""
    error_codes = loads(redis_client.get(config.REDIS_ERROR_CODES_KEY) or '{}')
    connection_types = loads(redis_client.get(config.REDIS_CONNECTION_TYPES_KEY) or '{}')
    hourly_errors = loads(redis_client.get(config.REDIS_HOURLY_ERRORS_KEY) or '{}')
    
    return {
        'error_codes': error_codes,
        'connection_types': connection_types,
        'hourly_errors': hourly_errors
    }

def update_stats(data, error_code):
    """Update statistics in Redis"""
    # Get current stats
    stats = get_stats()
    
    # Update error codes
    error_codes = stats['error_codes']
    error_codes[str(error_code)] = error_codes.get(str(error_code), 0) + 1
    redis_client.set(config.REDIS_ERROR_CODES_KEY, dumps(error_codes))
    
    # Update connection types
    connection_types = stats['connection_types']
    connection_types[data['connectionType']] = connection_types.get(data['connectionType'], 0) + 1
    redis_client.set(config.REDIS_CONNECTION_TYPES_KEY, dumps(connection_types))
    
    # Update hourly errors
    hour = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:00')
    hourly_errors = stats['hourly_errors']
    hourly_errors[hour] = hourly_errors.get(hour, 0) + 1
    redis_client.set(config.REDIS_HOURLY_ERRORS_KEY, dumps(hourly_errors))

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
        update_stats(data, error_code)
        
        # Store log in Redis
        logs = loads(redis_client.get(config.REDIS_LOGS_KEY) or '[]')
        logs.insert(0, data)
        if len(logs) > config.MAX_LOGS:
            logs.pop()
        redis_client.set(config.REDIS_LOGS_KEY, dumps(logs))
            
        return jsonify({"status": "success"}), 200
    except Exception as e:
        app.logger.error(f"Error processing webhook: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/logs')
def get_logs():
    logs = loads(redis_client.get(config.REDIS_LOGS_KEY) or '[]')
    return jsonify(logs)

@app.route('/stats')
def get_stats_endpoint():
    return jsonify(get_stats())

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