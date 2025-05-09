import subprocess
import time

# Your actual script filenames
scripts = [
    #'5paisa.py',
    'trendlyne1.py',
  #  'Equitymaster - Penny Stocks.py',
    'economic_times.py',
    'business_standard.py',
    'moneycontrol.py',
    #'Tbrain.py'
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
