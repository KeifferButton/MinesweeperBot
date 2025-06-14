import pyautogui
import time

print("Press Ctrl+C to stop.\n")

try:
    while True:
        x, y = pyautogui.position()
        print(f"Cursor position: ({x}, {y})", end='\r', flush=True)
        time.sleep(1)
except KeyboardInterrupt:
    print("\nStopped.")
