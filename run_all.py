# -*- coding: utf-8 -*-
"""
Created on Mon Oct 21 15:22:58 2024

@author: Saarit
"""


import subprocess
import os

# Define the correct path
cwd = "C:\\Users\\Saarit\\OneDrive\\Desktop\\Trading\\screener-algo-automation"
os.chdir(cwd)


scripts = [
    'et1_vol_selection.py',
    'et1_perchange_selection.py',
    'et1_rsi_60_rsidivergence_selection.py',
    'et1_significant_change_selection.py',
    'et1_papertrade.py',
    'et1_monitoring_papertrade.py',
]

for script in scripts:
    print(f"Running {script}...")
    result = subprocess.run(['python', script])
    if result.returncode != 0:
        print(f"Error occurred while running {script}. Exiting...")
        break


