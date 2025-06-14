import pyautogui

def main():
    print("Started")
    scanForField()



def scanForField():
    """TARGET COLOR:"""
    TARGETCOLOR = (189, 189, 189)
    
    # Get screen size
    screen_width, screen_height = pyautogui.size()
    
    # Take screenshot for performance reasons
    screenshot = pyautogui.screenshot()
    
    # Loop through every pixel (y then x) until target color is found
    for y in range(screen_height):
        for x in range(screen_width):
            if screenshot.getpixel((x, y)) == TARGETCOLOR:
                print(f"Found target color at ({x}, {y})")
                print(f"Adjacent colors are: UP: ({screenshot.getpixel((x, y - 1))}), LEFT: ({screenshot.getpixel((x - 1, y))}), DOWN: ({screenshot.getpixel((x, y + 1))}), RIGHT: ({screenshot.getpixel((x + 1, y))})")
                return


if __name__=="__main__":
    main()