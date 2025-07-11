import subprocess
import time
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Moneycontrol multi-script scraper is running."

def run_all_scripts():
    scripts = [
        'trendlyne1.py',
        'economic_times.py'
        
    ]

    delay_between_scripts = 15  # seconds
    processes = []

    for script in scripts:
        print(f"🚀 Launching {script}...")
        process = subprocess.Popen(['python', script])
        processes.append(process)
        time.sleep(delay_between_scripts)

    for process in processes:
        process.wait()

    print("✅ All scripts have finished running.")

if __name__ == "__main__":
    # Run the scripts once when server starts
    run_all_scripts()

    # Keep the server alive
    app.run(host="0.0.0.0", port=10000)
