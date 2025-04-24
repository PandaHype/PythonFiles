import itertools
import threading

# Character set
charset = 'aAbBcCdDeEfFgGhHiIjJkKlLmMnNoOpPqQrRsStTuUvVxXyYzZ0123456789!?$@'

# Output file
output_file = "combs.txt"

# Check if file is empty
try:
    with open(output_file, "r") as f:
        if f.read(1):
            print("File already has content. Skipping generation.")
            exit()
except FileNotFoundError:
    pass  # File doesn't exist, that's fine

# Thread-safe file writing
lock = threading.Lock()

def generate_and_write(length):
    with open(output_file, "a") as f:
        for combo in itertools.product(charset, repeat=length):
            combo_str = ''.join(combo) + '\n'
            with lock:
                f.write(combo_str)

# Start threads for lengths 1–5
threads = []
for length in range(1, 6):
    t = threading.Thread(target=generate_and_write, args=(length,))
    t.start()
    threads.append(t)

# Wait for all threads to finish
for t in threads:
    t.join()

print("Combination generation complete.")
