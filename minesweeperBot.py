"""
Designed to work on the following website:
https://minesweeperonline.com/#beginner
"""
# Inner boarder + 6 pixels

import pyautogui

def main():
    print("Started")
    board_coord = getGameLocation()
    print(f"Target color found at {board_coord}")


# Returns the top left corner of the game board
# Specifically the first pixel on the top left which is
# the specified TARGETCOLOR
def getGameLocation():
    """TARGET COLOR:"""
    TARGETCOLOR = (189, 189, 189)
    BACKGROUNDCOLOR = (255, 255, 255)
    
    # Get screen size
    screen_width, screen_height = pyautogui.size()
    
    # Take screenshot for performance reasons
    screenshot = pyautogui.screenshot()
    
    # Loop through every pixel (y then x) until target color is found
    for y in range(screen_height):
        for x in range(screen_width):
            # Test for target color at pixel (x, y)
            if screenshot.getpixel((x, y)) == TARGETCOLOR:
                # Test if down right pixel (x + 1, y + 1) is also target color
                # and check if up left pixel (x - 1, y - 1) is background color
                # to ensure pixel is actually from game board
                if screenshot.getpixel((x+1, y+1)) == TARGETCOLOR and screenshot.getpixel((x - 1, y - 1)) == BACKGROUNDCOLOR:
                    return (x, y)
          
    # Target color not found, return None   
    return None


if __name__=="__main__":
    main()