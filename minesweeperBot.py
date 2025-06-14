"""
Designed to work on the following website:
https://minesweeperonline.com/#beginner
"""
import pyautogui

"""TARGET COLOR:"""
TARGETCOLOR = (189, 189, 189)
BACKGROUNDCOLOR = (255, 255, 255)
TARGETDARK = (123, 123, 123)

def main():
    print("Started")
    
    # Locate game board on screen
    board_coord = getGameLocation()
    if board_coord == None:
        print("Error: Failed to locate game board")
        return 1
    print(f"Target color found at {board_coord}")
    
    # Get first tile location and tile width
    tile_coord, tile_width = getTileInfo(board_coord)

# Returns the top left corner of the first tile
# and the width of each tile
def getTileInfo(board_coord):
    x, y = board_coord
    screenshot = pyautogui.screenshot()
    
    # Find inner corner of top menu (has correct x coordinate)
    while screenshot.getpixel((x, y)) != TARGETDARK:
        #print(f"Color: {screenshot.getpixel((x, y))} found at ({x}, {y})")
        x += 1
        y += 1
    while screenshot.getpixel((x, y)) != TARGETCOLOR:
        x += 1
        y += 1
    
    print(x, y)
    print(f"Left: {screenshot.getpixel(x - 1, y)}, Up: {screenshot.getpixel(x, y - 1)}")
    
    return None, None

# Returns the top left corner of the game board
# Specifically the first pixel on the top left which is
# the specified TARGETCOLOR
def getGameLocation():
    # Get screen size
    screen_width, screen_height = pyautogui.size()
    
    # Take screenshot for performance reasons
    screenshot = pyautogui.screenshot()
    
    # Loop through every pixel (y then x) until target color is found
    for y in range(screen_height):
        for x in range(screen_width):
            # Test for target color at pixel (x, y)
            if screenshot.getpixel((x, y)) == TARGETCOLOR:
                print(f"Found at ({x}, {y})")
                # Test if down right pixel (x + 1, y + 1) is also target color
                # and check if up left pixel (x - 1, y - 1) is background color
                # to ensure pixel is actually from game board
                if screenshot.getpixel((x+1, y+1)) == TARGETCOLOR and screenshot.getpixel((x - 1, y - 1)) == BACKGROUNDCOLOR:
                    # Bug is that pixels are larger than they appear so top right sticking out portion counts
                    # To fix loop down right until dark pixel is found to confirm
                    print(screenshot.getpixel((x-2, y-2)), screenshot.getpixel((x-1, y-2)), screenshot.getpixel((x, y-2)), screenshot.getpixel((x+1, y-2)), screenshot.getpixel((x+2, y-2)), "\n",
                        screenshot.getpixel((x-2, y-1)), screenshot.getpixel((x-1, y-1)), screenshot.getpixel((x, y-1)), screenshot.getpixel((x+1, y-1)), screenshot.getpixel((x+2, y-1)), "\n",
                          screenshot.getpixel((x-2, y)), screenshot.getpixel((x-1, y)), screenshot.getpixel((x, y)), screenshot.getpixel((x+1, y)), screenshot.getpixel((x+2, y)), "\n",
                          screenshot.getpixel((x-2, y+1)), screenshot.getpixel((x-1, y+1)), screenshot.getpixel((x, y+1)), screenshot.getpixel((x+1, y+1)), screenshot.getpixel((x+2, y+1)), "\n",
                          screenshot.getpixel((x-2, y+2)), screenshot.getpixel((x-1, y+2)), screenshot.getpixel((x, y+2)), screenshot.getpixel((x+1, y+2)), screenshot.getpixel((x+2, y+2)))
                    return (x, y)
          
    # Target color not found, return None   
    return None

if __name__=="__main__":
    main()