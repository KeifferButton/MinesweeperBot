"""
Designed to work on the following website:
https://minesweeperonline.com/#beginner

Works on 100% and 200% scale but not 150% because it uses slightly different
colors so game board location logic would need to be changed
"""
import pyautogui

"""TARGET COLOR:"""
TARGETCOLOR = (189, 189, 189)       # Border color of game
BACKGROUNDCOLOR = (255, 255, 255)   # Background color of website (default white)
TARGETDARK = (123, 123, 123)        # Darker border color of game
TARGETBACK = (192, 192, 192)        # Interior background of game which is slightly different that TARGETCOLOR for some reason

def main():
    print("Started")
    
    # Locate game board on screen
    board_coord = getGameLocation()
    if board_coord == None:
        print("Error: Failed to locate game board")
        return 1
    
    # Get first tile location and tile width
    tile_coord, tile_width = getTileInfo(board_coord)

# Returns the top left corner of the first tile
# and the width/height of each tile
def getTileInfo(board_coord):
    x, y = board_coord
    screenshot = pyautogui.screenshot()
    
    # Find inner corner of top menu (has correct x coordinate)
    while screenshot.getpixel((x, y)) != TARGETDARK:    # Move through TARGETCOLOR to TARGETDARK (technically redundant with next while but left in for understandability)
        x += 1
        y += 1
    while screenshot.getpixel((x, y)) != TARGETBACK:    # Move through TARGETDARK to TARGETBACK
        x += 1
        y += 1
    
    # Move downwards until the top left white pixel of the first tile is located
    while screenshot.getpixel((x, y)) != BACKGROUNDCOLOR:   # Move to white border
        y += 1
    while screenshot.getpixel((x, y)) != TARGETDARK:        # Move past white to dark
        y += 1
    while screenshot.getpixel((x, y)) != BACKGROUNDCOLOR:   # Move until white reached again which should be the tile corner
        y += 1
    
    # Tile corner found
    tile_coord = (x, y)
    
    # Move right to next tile to determine width
    while screenshot.getpixel((x, y)) != TARGETCOLOR:       # There is one pixel of TARGETCOLOR so first move there
        x += 1
    while screenshot.getpixel((x, y)) != BACKGROUNDCOLOR:   # Move past TARGETCOLOR to next tile
        x += 1
    
    # Width and height are equal since tiles are square
    width = x - tile_coord[0]
    
    return tile_coord, width

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
                # Test if down right pixel (x + 1, y + 1) is also target color
                # and check if up left pixel (x - 1, y - 1) is background color
                # to ensure pixel is actually from game board
                if screenshot.getpixel((x + 1, y + 1)) == TARGETCOLOR and screenshot.getpixel((x - 1, y - 1)) == BACKGROUNDCOLOR:
                    # Loop through pixels of the same color
                    offset = 2
                    while screenshot.getpixel((x + offset, y + offset)) == TARGETCOLOR and offset <= 52 and x + offset < screen_width and y + offset < screen_height:
                        offset += 1
                    
                    # If next pixel is TARGETDARK then loop through them until next color is found, otherwise continue
                    if x + offset < screen_width and y + offset < screen_height and screenshot.getpixel((x + offset, y + offset)) == TARGETDARK:
                        while screenshot.getpixel((x + offset, y + offset)) == TARGETDARK and offset <= 52 and x + offset < screen_width and y + offset < screen_height:
                            offset += 1
                        
                        # Once through TARGETDARK, if next pixel is TARGETBACK then board found, otherwise continue
                        if x + offset < screen_width and y + offset < screen_height and screenshot.getpixel((x + offset, y + offset)) == TARGETBACK:
                            return (x, y)
                        else:
                            continue
                    else:
                        continue
          
    # Target color not found, return None   
    return None

if __name__=="__main__":
    main()