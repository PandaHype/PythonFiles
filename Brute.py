import tkinter as tk
import time
import psutil
import os
import threading

p = psutil.Process(os.getpid())
p.nice(psutil.HIGH_PRIORITY_CLASS)


# Correct password we're trying to guess
correct_password = 'a@@@'

# Read guesses from file, strip newlines
with open("combs.txt", "r") as f:
    guesses = [line.strip() for line in f]

guess_index = 0
found = False
start_time = None
elapsed_time = None

def get_input():
    global found
    user_input = entry.get()
    if guess_index % 10000 == 0:
        print("Guess Count:", guess_index)

    if user_input == correct_password:
        result_label.config(text="Password Found!") 
        found = True

def update_gps():
    global start_time, guess_index
    if start_time is None:
        return

    elapsed = time.time() - start_time
    if elapsed > 0:
        elapsed_time_label.config(text=f"Elapsed Time: {elapsed:.2f} seconds")
        gps = guess_index / elapsed
        gps_label.config(text=f"Guesses per second: {gps:.2f}")

    if not found and guess_index < len(guesses):
        screen.after(1000, update_gps) 

def brute_force():
    global guess_index, start_time

    if start_time is None:
        start_time = time.time()
        screen.after(1000, update_gps)

    if not found and guess_index < len(guesses):
        current_guess = guesses[guess_index]
        entry.delete(0, tk.END)
        entry.insert(0, current_guess)
        get_input()
        guess_index += 1
        screen.after(0,brute_force)
    elif not found:
        result_label.config(text="All guesses tried.")

# GUI setup
screen = tk.Tk()
screen.title('Login Screen')

entry = tk.Entry(screen, width=30)
entry.pack(pady=10)

submit_button = tk.Button(screen, text="Submit", command=get_input)
submit_button.pack()

start_button = tk.Button(screen, text="Start Brute Force", command=brute_force)
start_button.pack()

result_label = tk.Label(screen, text="")
result_label.pack()

gps_label = tk.Label(screen, text="Guesses per second: 0.00")
gps_label.pack()

elapsed_time_label = tk.Label(screen, text="Elapsed Time: 0.00 seconds")
elapsed_time_label.pack()

screen.mainloop()
