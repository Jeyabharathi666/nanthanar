import subprocess
import time

# Your actual script filenames
scripts = [
    'trendlyne1.py',
    'economic_times.py',
    'sheshaview.py',
    'business_standard.py',
    'moneycontrol.py'
]

# Delay between launching each script (in seconds)
delay_between_scripts = 15  # Adjust if needed (e.g., 10–30 seconds)

processes = []

# Start scripts with delay
for script in scripts:
    print(f"🚀 Launching {script}...")
    process = subprocess.Popen(['python', script])
    processes.append(process)
    time.sleep(delay_between_scripts)  # ⏳ Delay before next script

# Wait for all to finish
for process in processes:
    process.wait()

print("✅ All scripts have finished running.")
