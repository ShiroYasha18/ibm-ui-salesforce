from flask import Flask, request, jsonify, send_from_directory
import threading
import time
import random
import os
import datetime
import json
import sys

# Create a logs directory
if not os.path.exists('logs'):
    os.makedirs('logs')

# Set up log file
log_file_path = os.path.join('logs', f"server_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
log_file = open(log_file_path, 'w')

def log(message, level="INFO"):
    """Log a message to both console and log file"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_message = f"[{timestamp}] [{level}] {message}"
    
    # Print to console
    print(formatted_message, flush=True)  # Ensure it's printed immediately
    
    # Write to log file
    log_file.write(formatted_message + "\n")
    log_file.flush()  # Ensure it's written immediately

app = Flask(__name__)

# Global variables
current_html = 'index'
last_extracted_html = ''
detection_queue = []
simulation_running = False
log_data = []

# Paths to HTML files
HTML_FILES = {
    'index': 'index_xpath_test.html',
    'alternative': 'alternative_xpath_test.html'
}

# Serve static files
@app.route('/')
def index():
    log(f"Serving index page with current HTML: {current_html}")
    return send_from_directory('.', HTML_FILES[current_html])

@app.route('/script.js')
def script():
    log("Serving script.js")
    return send_from_directory('.', 'script.js')

# Health check endpoint
@app.route('/health')
def health():
    log("Health check requested")
    return jsonify({'status': 'ok'})

# API endpoint to switch HTML
@app.route('/switch-html', methods=['POST'])
def switch_html():
    global current_html
    data = request.json
    
    if 'html' in data and data['html'] in HTML_FILES:
        current_html = data['html']
        log(f"HTML switched to: {current_html}")
        log_event('html_changed', {'new_html': current_html})
        return jsonify({'success': True})
    
    log(f"Invalid HTML type requested: {data.get('html')}", "WARNING")
    return jsonify({'success': False, 'error': 'Invalid HTML type'})

# API endpoint to check for detections
@app.route('/check-detections', methods=['GET'])
def check_detections():
    if detection_queue:
        detection = detection_queue.pop(0)
        log(f"Reporting detection: {detection}")
        return jsonify({'detected': True, 'timestamp': detection})
    return jsonify({'detected': False})

# HTML Extractor function
def html_extractor():
    global last_extracted_html, detection_queue
    
    log("HTML extractor started")
    
    while simulation_running:
        try:
            # Simulate extracting HTML from the website
            with open(HTML_FILES[current_html], 'r') as file:
                current_extracted_html = file.read()
            
            # Check if HTML has changed
            if last_extracted_html and current_extracted_html != last_extracted_html:
                timestamp = datetime.datetime.now().isoformat()
                detection_queue.append(timestamp)
                log(f"HTML change detected at {timestamp}")
                log_event('change_detected', {'timestamp': timestamp})
            else:
                log("HTML extractor check - No changes detected")
            
            # Update last extracted HTML
            last_extracted_html = current_extracted_html
            
        except Exception as e:
            log(f"Error in HTML extractor: {e}", "ERROR")
        
        # Wait for 20 seconds before next extraction
        log("HTML extractor waiting for next check (20 seconds)")
        time.sleep(20)

# Log events to file
def log_event(event_type, data):
    event = {
        'timestamp': datetime.datetime.now().isoformat(),
        'type': event_type,
        'data': data
    }
    log_data.append(event)
    
    # Write to log file
    with open('simulation_log.json', 'w') as f:
        json.dump(log_data, f, indent=2)
    
    log(f"Event logged: {event_type} - {data}")

# Start the simulation
@app.route('/start-simulation', methods=['POST'])
def start_simulation():
    global simulation_running, log_data
    
    if simulation_running:
        log("Attempt to start simulation when already running", "WARNING")
        return jsonify({'success': False, 'error': 'Simulation already running'})
    
    data = request.json
    duration = data.get('duration', 2)  # Default 10 minutes
    
    log(f"Starting simulation with duration: {duration} minutes")
    
    # Reset simulation data
    simulation_running = True
    log_data = []
    
    # Log start event
    log_event('simulation_started', {'duration': duration})
    
    # Start HTML extractor in a separate thread
    extractor_thread = threading.Thread(target=html_extractor)
    extractor_thread.daemon = True
    extractor_thread.start()
    log("HTML extractor thread started")
    
    # Schedule simulation end
    def end_simulation():
        global simulation_running
        log(f"Simulation end scheduled for {duration} minutes from now")
        time.sleep(duration * 60)  # Convert minutes to seconds
        if simulation_running:
            simulation_running = False
            log("Simulation ended automatically after scheduled duration")
            log_event('simulation_ended', {'status': 'completed'})
    
    end_thread = threading.Thread(target=end_simulation)
    end_thread.daemon = True
    end_thread.start()
    log("Simulation end scheduler thread started")
    
    return jsonify({'success': True})

# Stop the simulation
@app.route('/stop-simulation', methods=['POST'])
def stop_simulation():
    global simulation_running
    
    if not simulation_running:
        log("Attempt to stop simulation when not running", "WARNING")
        return jsonify({'success': False, 'error': 'No simulation running'})
    
    simulation_running = False
    log("Simulation stopped manually")
    log_event('simulation_ended', {'status': 'stopped_manually'})
    
    return jsonify({'success': True})

# Get simulation report
@app.route('/simulation-report', methods=['GET'])
def get_report():
    # Count events
    html_changes = sum(1 for event in log_data if event['type'] == 'html_changed')
    detections = sum(1 for event in log_data if event['type'] == 'change_detected')
    
    # Calculate accuracy
    accuracy = (detections / html_changes * 100) if html_changes > 0 else 0
    
    report = {
        'total_changes': html_changes,
        'detected_changes': detections,
        'accuracy': round(accuracy, 2),
        'log_data': log_data
    }
    
    log(f"Report generated - Changes: {html_changes}, Detections: {detections}, Accuracy: {accuracy:.2f}%")
    
    return jsonify(report)

if __name__ == '__main__':
    log("Starting Flask server on port 5000")
    app.run(debug=False, port=5000)  # Set debug=False to avoid duplicate log messages