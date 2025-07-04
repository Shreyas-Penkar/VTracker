import time, sys
from termcolor import colored

# Spinner animation function
def loading_spinner(msg, stop_event):
    spinner = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    idx = 0
    while not stop_event.is_set():
        spin_char = colored(spinner[idx % len(spinner)], 'green')
        sys.stdout.write(f"\r{colored(msg, 'green')} {spin_char}")
        sys.stdout.flush()
        idx += 1
        time.sleep(0.1)
    sys.stdout.write("\r" + " " * (len(msg) + 4) + "\r")  # clear line


