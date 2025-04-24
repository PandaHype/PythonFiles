import tkinter as tk
import time
import threading
import os
import mmap
import psutil

# System priority boost (Windows only)
p = psutil.Process(os.getpid())
p.nice(psutil.HIGH_PRIORITY_CLASS)

file_path = "combs.txt"
correct_password = "@@@@"  # What we’re trying to crack

found = False
guess_count = 0
start_time = None
found_lock = threading.Lock()

# GUI setup
screen = tk.Tk()
screen.title("Multithreaded Brute Force")

entry = tk.Entry(screen, width=30)
entry.pack(pady=10)

submit_button = tk.Button(screen, text="Submit")
submit_button.pack()

start_button = tk.Button(screen, text="Start Brute Force")
start_button.pack()

result_label = tk.Label(screen, text="")
result_label.pack()

gps_label = tk.Label(screen, text="Guesses per second: 0.00")
gps_label.pack()

elapsed_time_label = tk.Label(screen, text="Elapsed Time: 0.00 seconds")
elapsed_time_label.pack()

# Manual input
def check_manual_guess():
    global found
    user_input = entry.get()
    if user_input == correct_password:
        found = True
        result_label.config(text="Password Found Manually!")

submit_button.config(command=check_manual_guess)

# Update stats
def update_gps():
    global guess_count, start_time
    if not start_time:
        return
    elapsed = time.time() - start_time
    gps = guess_count / elapsed if elapsed > 0 else 0
    gps_label.config(text=f"Guesses per second: {gps:.2f}")
    elapsed_time_label.config(text=f"Elapsed Time: {elapsed:.2f} seconds")
    if not found:
        screen.after(100, update_gps)

# Chunked line reading + guessing using mmap
def read_and_guess_chunk(start, end):
    global guess_count, found
    with open(file_path, "r") as f:
        # Memory-map the file
        mmapped_file = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        
        # Make sure we start at the right position
        mmapped_file.seek(start)

        # Read lines within the chunk range
        while mmapped_file.tell() < end:
            if found:
                return

            # Read one line at a time
            line = mmapped_file.readline()
            if not line:
                break

            try:
                guess = line.decode(errors="ignore").strip()
            except:
                continue

            with found_lock:
                guess_count += 1
                if guess == correct_password:
                    found = True
                    screen.after(0, lambda: result_label.config(text=f"Password Found: {guess}"))
                    return

# Brute-force entry point
def start_brute_force():
    global start_time, found, guess_count
    found = False
    guess_count = 0
    start_time = time.time()

    file_size = os.path.getsize(file_path)
    num_threads = 1
    chunk_size = file_size // num_threads
    threads = []

    for i in range(num_threads):
        start = i * chunk_size
        end = file_size if i == num_threads - 1 else (i + 1) * chunk_size
        t = threading.Thread(target=read_and_guess_chunk, args=(start, end), daemon=True)
        t.start()
        threads.append(t)

    update_gps()

start_button.config(command=start_brute_force)
screen.mainloop()
