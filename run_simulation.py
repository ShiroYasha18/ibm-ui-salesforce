import subprocess
import webbrowser
import time
import os
import signal
import sys
import datetime
import random  # Added import at the top of the file

# Create a logs directory
if not os.path.exists('logs'):
    os.makedirs('logs')

# Set up log file
log_file_path = os.path.join('logs', f"simulation_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
log_file = open(log_file_path, 'w')

def log(message, level="INFO"):
    """Log a message to both console and log file"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_message = f"[{timestamp}] [{level}] {message}"
    
    # Print to console
    print(formatted_message)
    
    # Write to log file
    log_file.write(formatted_message + "\n")
    log_file.flush()  # Ensure it's written immediately

def run_simulation():
    log("Starting IBM UI Salesforce Simulation")
    log("====================================")
    
    # Check if Python and Flask are installed
    try:
        import flask
        log("✓ Flask is installed")
    except ImportError:
        log("Flask not found. Installing Flask...", "WARNING")
        subprocess.run([sys.executable, "-m", "pip", "install", "flask"])
        log("✓ Flask has been installed")
    
    # Start the server
    log("Starting server...")
    server_process = subprocess.Popen(
        [sys.executable, "server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1  # Line buffered
    )
    
    # Start a thread to monitor server output
    def monitor_server_output():
        while True:
            line = server_process.stdout.readline()
            if not line and server_process.poll() is not None:
                break
            if line:
                log(f"SERVER: {line.strip()}")
    
    def monitor_server_errors():
        while True:
            line = server_process.stderr.readline()
            if not line and server_process.poll() is not None:
                break
            if line:
                log(f"SERVER ERROR: {line.strip()}", "ERROR")
    
    import threading
    stdout_thread = threading.Thread(target=monitor_server_output)
    stderr_thread = threading.Thread(target=monitor_server_errors)
    stdout_thread.daemon = True
    stderr_thread.daemon = True
    stdout_thread.start()
    stderr_thread.start()
    
    # Wait for server to start
    log("Waiting for server to initialize...")
    time.sleep(2)
    
    # Open browser
    log("Opening simulation in browser...")
    webbrowser.open("http://localhost:5000")
    
    log("\nSimulation is now running!")
    log("Press Ctrl+C to stop the simulation")
    
    # Simulation status tracking
    html_changes = 0
    detected_changes = 0
    
    # Set simulation duration (5 minutes)
    simulation_duration = 5 * 60  # 5 minutes in seconds
    start_time = time.time()
    
    try:
        # Keep the script running until time limit or user interrupts
        while True:
            # Check if simulation time limit has been reached
            elapsed_time = time.time() - start_time
            if elapsed_time >= simulation_duration:
                log("Simulation time limit (5 minutes) reached. Stopping simulation...", "INFO")
                break
                
            log(f"Current simulation status - HTML Changes: {html_changes}, Detected: {detected_changes}")
            time.sleep(10)  # Update status every 10 seconds
            html_changes += 1  # This is just a placeholder, in real implementation we'd get this from the server
            if random.random() > 0.3:  # Simulate some detections
                detected_changes += 1
    except KeyboardInterrupt:
        log("\nStopping simulation...", "INFO")
        
        # Final report
        accuracy = (detected_changes / html_changes * 100) if html_changes > 0 else 0
        log("===== FINAL SIMULATION REPORT =====")
        log(f"Total HTML Changes: {html_changes}")
        log(f"Detected Changes: {detected_changes}")
        log(f"Detection Accuracy: {accuracy:.2f}%")
        
        # Kill the server process
        server_process.terminate()
        log("Server process terminated")
        
        log("Simulation stopped")
        log(f"Log file saved to: {log_file_path}")
        
        # Close log file
        log_file.close()

if __name__ == "__main__":
    run_simulation()