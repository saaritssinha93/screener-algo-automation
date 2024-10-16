# -*- coding: utf-8 -*-
"""
Created on Wed Oct 16 10:20:47 2024

@author: Saarit
"""



import tkinter as tk
from tkinter import messagebox

# Create the root window
root = tk.Tk()
root.withdraw()  # Hide the root window

# Show an alert message box
messagebox.showinfo("Information", "This is an info pop-up")







import tkinter as tk
from tkinter import messagebox

root = tk.Tk()
root.withdraw()  # Hide the root window

# Show a warning pop-up
messagebox.showwarning("Warning", "This is a warning pop-up")

# Show an error pop-up
messagebox.showerror("Error", "This is an error pop-up")





import tkinter as tk
from tkinter import messagebox

root = tk.Tk()
root.withdraw()  # Hide the root window

# Ask a Yes/No question
response = messagebox.askyesno("Question", "Do you want to proceed?")
if response:
    print("User clicked Yes")
else:
    print("User clicked No")







import tkinter as tk

def create_output_window(output_text):
    # Create the main window
    root = tk.Tk()
    root.title("Output Window")

    # Create a text widget to display output
    text_widget = tk.Text(root, height=20, width=50)
    text_widget.pack(padx=10, pady=10)

    # Insert the output text into the widget
    text_widget.insert(tk.END, output_text)

    # Make the text widget read-only
    text_widget.config(state=tk.DISABLED)

    # Start the Tkinter event loop
    root.mainloop()

# Example output to display in the window
output = "This is the output of your program!\nMore lines of text can be added here."

# Call the function to create the window
create_output_window(output)






import tkinter as tk
import threading
import time

# Function to create the output window
def create_output_window(output_text):
    root = tk.Tk()
    root.title("Output Window")

    # Create a text widget to display output
    text_widget = tk.Text(root, height=20, width=50)
    text_widget.pack(padx=10, pady=10)

    # Insert initial output text into the widget
    text_widget.insert(tk.END, output_text)
    text_widget.config(state=tk.DISABLED)  # Make text read-only

    # Update output dynamically
    def update_output(new_text):
        text_widget.config(state=tk.NORMAL)  # Unlock the text widget
        text_widget.insert(tk.END, new_text)  # Insert new text
        text_widget.config(state=tk.DISABLED)  # Lock the text widget again

    # Start the Tkinter event loop
    root.mainloop()

# Function to run code in the background
def background_task(update_output):
    # Simulating long-running background work
    for i in range(1, 11):
        time.sleep(2)  # Simulate work
        output_text = f"Task iteration {i} completed.\n"
        update_output(output_text)

# Run Tkinter window and background task concurrently
def run_program():
    # Start the output window in a separate thread
    output_thread = threading.Thread(target=create_output_window, args=("Initial output...\n",))
    output_thread.start()

    # Background task to run simultaneously
    background_task_thread = threading.Thread(target=background_task, args=(print,))
    background_task_thread.start()

if __name__ == "__main__":
    run_program()
