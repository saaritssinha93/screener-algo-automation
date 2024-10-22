# -*- coding: utf-8 -*-
"""
Created on Mon Oct 21 15:22:58 2024

@author: Saarit
"""

import subprocess
import os
import time
import schedule
from datetime import datetime

# Define the correct path
cwd = "C:\\Users\\Saarit\\OneDrive\\Desktop\\Trading\\screener-algo-automation"
os.chdir(cwd)

# Path to monitor for data change
significant_change_file = "significant_change_data.txt"  # Assumed file for tracking data changes
previous_file_size = 0

# Function to check if significant data has changed
def has_data_changed(file_path):
    global previous_file_size
    try:
        current_file_size = os.path.getsize(file_path)
        if current_file_size != previous_file_size:
            previous_file_size = current_file_size
            return True
        return False
    except FileNotFoundError:
        return False

# Function to run scripts sequentially and every 30 minutes
def run_sequential_scripts():
    scripts = [
        'et1_perchangefirst_selection.py',
        'et1_vol_second_selection.py',
        'et1_rsi_60_rsidivergence_selection.py',
    ]
    
    for script in scripts:
        print(f"Running {script}...")
        result = subprocess.run(['python', script])
        if result.returncode != 0:
            print(f"Error occurred while running {script}. Exiting...")
            break

# Function to run 'et1_significant_change_selection.py' continuously
def run_significant_change_script():
    while datetime.now().time() < datetime.strptime("15:30", "%H:%M").time():
        print("Running 'et1_significant_change_selection.py'...")
        result = subprocess.run(['python', 'et1_significant_change_selection.py'])
        if result.returncode != 0:
            print(f"Error occurred while running 'et1_significant_change_selection.py'.")
            break
        time.sleep(10)  # Short delay between each execution

# Function to run 'et1_papertrade.py' only if data changed
def run_papertrade_if_data_changed():
    if has_data_changed(significant_change_file):
        print("Data change detected, running 'et1_papertrade.py'...")
        result = subprocess.run(['python', 'et1_papertrade.py'])
        if result.returncode != 0:
            print(f"Error occurred while running 'et1_papertrade.py'.")
            return True  # Indicating that 'et1_papertrade.py' ran
    return False

# Function to manage 'et1_monitoring_papertrade_multiwindow_live.py'
def run_monitoring_if_papertrade_executed():
    monitoring_active = False

    while datetime.now().time() < datetime.strptime("15:30", "%H:%M").time():
        if run_papertrade_if_data_changed():
            if not monitoring_active:
                print("Starting 'et1_monitoring_papertrade_multiwindow_live.py'...")
                monitoring_process = subprocess.Popen(['python', 'et1_monitoring_papertrade_multiwindow_live.py'])
                monitoring_active = True

        # If 'et1_papertrade.py' is not running and monitoring is active, stop monitoring
        if not has_data_changed(significant_change_file) and monitoring_active:
            print("Stopping 'et1_monitoring_papertrade_multiwindow_live.py'...")
            monitoring_process.terminate()
            monitoring_active = False
        
        time.sleep(5)  # Small delay between checks

# Schedule tasks
schedule.every().day.at("09:15").do(run_sequential_scripts)
schedule.every(30).minutes.do(run_sequential_scripts)
schedule.every().day.at("09:20").do(run_significant_change_script)

# Main execution loop
if __name__ == "__main__":
    while datetime.now().time() < datetime.strptime("15:30", "%H:%M").time():
        schedule.run_pending()
        run_monitoring_if_papertrade_executed()  # Continuously check if 'et1_papertrade.py' ran and manage monitoring
        time.sleep(1)
