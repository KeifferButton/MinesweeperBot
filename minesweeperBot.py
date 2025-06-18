"""
Designed to work on the following website:
https://minesweeperonline.com

Works on 100% and 200% scale but not 150% because it uses slightly different
colors so game board location logic would need to be changed
"""
import pyautogui
pyautogui.PAUSE = 0.015
import sys
import time
import copy
import keyboard
import random

"""TARGET COLOR:"""
TARGETCOLOR = (189, 189, 189)       # Border color of game
BACKGROUNDCOLOR = (255, 255, 255)   # Background color of website (default white)
TARGETDARK = (123, 123, 123)        # Darker border color of game
TARGETBACK = (192, 192, 192)        # Interior background of game which is slightly different that TARGETCOLOR for some reason

'''FORCE EXIT KEY'''
EXITKEY = 'esc'

'''
Goals:
Allow program to start clicking at beginning (determine best location to click for start or do random)
Complete chooseBestAction with deep scan / guessing mode
Improve visuals be removing previous prints, also add statistics
Add looping mode in seperate file which tracks wins vs losses (will require exiting name enter menu)
'''

def main():
    print("Started")
    
    # Locate game board on screen
    board_coord = getGameLocation()
    if board_coord == None:
        print("Error: Failed to locate game board")
        return 1
    
    # Get first tile location and tile width
    tile_coord, tile_width = getTileInfo(board_coord)
    
    # Determine size of game board
    board_width, board_height = getBoardSize(tile_coord, tile_width)
    print(board_width, "x", board_height)
    
    # 2D matrix which will store the state of each tile
    game_matrix = [[None for _ in range(board_width)] for _ in range (board_height)]
    
    # Get the location of the smiley face
    life_pix1, life_pix2 = getLifeLocation(board_coord, tile_coord)
    
    #input("Please update gamestate")
    
    counter = 0
    doScan = False
    while True:
        # If EXITKEY is held, quit
        checkForForceExit()
        
        print("Loop:", counter)
        counter += 1
        
        # Break if dead or have won
        life = checkForWin(life_pix1, life_pix2)
        if life != 0:
            break
        
        pyautogui.moveTo(board_coord)
        if doScan:
            if getGameState(game_matrix, board_width, board_height, tile_coord, tile_width) == 1:
                print("Failed to scan")
        doScan = True
        
        print('\n'.join([' '.join(map(str, row)) for row in game_matrix]).replace("None", "☐").replace("0", " ").replace("-1", "^"))
        
        if counter == 1:
            # If first round, click a random location
            clickTile((random.randint(0, board_width - 1), random.randint(0, board_height - 1)), False, board_width, board_height, tile_coord, tile_width)
        else:
            action, rClick, chance = chooseBestAction(game_matrix, board_width, board_height)
            
            if rClick:
                doScan = False
            
            clickTile(action, rClick, board_width, board_height, tile_coord, tile_width)
        
        
def checkForForceExit():
    try:
        if keyboard.is_pressed(EXITKEY):
            print("Emergency stop triggered")
            sys.exit(0)
    except:
        pass 
    
# gets the position of the yellow smiley face which determines whether you're alive, dead, or have won
# Return value:
# tuple pix1 (int x, int y): The coordinates of a pixel which needs to be checked (x + 6, y - 3)
# tuple pix2 (int x, int y): The coordinates of a pixel which needs to be checked (x + 4, y - 1)
def getLifeLocation(board_coord, tile_coord):
    screenshot = pyautogui.screenshot()
    
    # Align coords with smiley
    x = tile_coord[0]
    y = (board_coord[1] + tile_coord[1]) // 2
    
    # Move right until yellow detected
    while screenshot.getpixel((x, y)) != (255, 255, 0):
        x += 1
        
    # Once yellow is hit, move back until off black to get how many real pixels make up one smiley pixel
    pixelSize = 0
    x -= 1
    while screenshot.getpixel((x, y)) == (0, 0, 0):
        x -= 1
        pixelSize += 1
       
    x += 1
       
    # Return pixels to be checked
    pix1 = (x + 6 * pixelSize, y + 3 * pixelSize)
    pix2 = (x + 4 * pixelSize, y + pixelSize)
    
    return pix1, pix2
    
# Determines whether you're alive, dead, or have won the game
# Return values:
# 0: alive
# 1: dead
# 2: won
def checkForWin(pix1, pix2):
    screenshot = pyautogui.screenshot()
    
    # If at pixel (x + 6, y - 3) there is black, then still alive or win. (technically y + 3 because down is positive)
    if screenshot.getpixel(pix1) == (0, 0, 0):
        # If at pixel (x + 4, y - 1) there is black, then alive
        if screenshot.getpixel(pix2) == (0, 0, 0):
            return 0
        # Otherwise, win
        else:
            return 2
    # Otherwise, dead
    else:
        return 1
    

# Determines the best next action with the highest probability of living
# Return values:
# tuple tile: (int x, int y):   The tile coordinate to click
# boolean rClick:               True when action is right click (to place flag)
# float chance:                 The probability of staying alive after the click. 0 when 100% survival rate
def chooseBestAction(game_matrix, board_width, board_height):
    # Quick scan for any obvious actions
    for y in range(board_height):
        for x in range(board_width):
            # Count up number of flags and up tiles around number tile
            if game_matrix[y][x] != None and game_matrix[y][x] != -1:
                flags = up = 0
                for j in range(-1, 2):
                    for i in range(-1, 2):
                        # Bounds check
                        if y + j < 0 or y + j >= board_height or x + i < 0 or x + i >= board_width:
                            continue
                        
                        if j != 0 or i != 0:
                            value = game_matrix[y + j][x + i]
                            # Up tile
                            if value == None:
                                up += 1
                            # Flag
                            elif value == -1:
                                flags += 1
                
                # Easy action detected
                if flags == game_matrix[y][x] or (up > 0 and flags + up == game_matrix[y][x]):
                    useFlag = True
                    # If the number of flags == the tile number, then the rest of the tiles must not be bombs
                    if flags == game_matrix[y][x]:
                        useFlag = False
                    # Otherwise, the number of flags + up tiles == the tile number, then the rest of the up tiles must be bombs
                    
                    # Scan for first tile meeting useFlag requirement
                    for j in range(-1, 2):
                        for i in range(-1, 2):
                            # Bounds check
                            if y + j < 0 or y + j >= board_height or x + i < 0 or x + i >= board_width:
                                continue
                            
                            value = game_matrix[y + j][x + i]
                            
                            # If up tile found
                            if value == None:
                                # Plant flag
                                if useFlag:
                                    game_matrix[y + j][x + i] = -1
                                    return (x + i, y + j), True, 0.0
                                # Dig tile
                                else:
                                    return (x + i, y + j), False, 0.0
    
    
    # If no obvious actions found by quick scan:
    # Deep scan: Checks all possible bomb layouts, sums them for each tile, and returns the tile with 
    # the fewest total bombs across all possibilities aka with the lowest probability of death
    
    # Matrix which stores the number of times each tile contains a bomb out of all valid arrangements
    bomb_matrix = [[None for _ in range(board_width)] for _ in range (board_height)]
    # Set of all not flagged up tiles adjacent to a number tile
    up_tiles = set()
    # Number of valid arrangements discovered
    valid_arrangements = [0]
    
    # Loop through every number tile
    for y in range(board_height):
        for x in range(board_width):
            if game_matrix[y][x] != None and game_matrix[y][x] != -1:
                # Create a set of all up tiles (not flagged) adjacent to a number tile
                for j in range(-1, 2):
                    for i in range(-1, 2):
                        # Bounds check
                        if y + j < 0 or y + j >= board_height or x + i < 0 or x + i >= board_width:
                            continue
                        
                        if (j != 0 or i != 0) and game_matrix[y + j][x + i] == None:
                            up_tiles.add((x + i, y + j))
     
    # Set used by checkAllLayouts which stores coordinates of tiles set as containing a bomb
    bomb_set = set()
    # Check all possible bomb layouts and set valid layouts to bomb_matrix
    checkAllLayouts(game_matrix, bomb_matrix, up_tiles, bomb_set, board_width, board_height, valid_arrangements)
    
    # Find best action where bomb_matrix has the fewest possible bombs
    min_bombs = float('inf')
    min_tile = (-1, -1)
    for y in range(board_height):
        for x in range(board_width):
            if game_matrix[y][x] is None and bomb_matrix[y][x] is not None and bomb_matrix[y][x] < min_bombs:
                min_bombs = bomb_matrix[y][x]
                min_tile = (x, y)
    
    # Determine probability of staying alive after action
    probability = 0
    if min_bombs > 0 and valid_arrangements[0] > 0:
        probability = min_bombs / valid_arrangements[0]
        
    print(f"Valid arrangements: {valid_arrangements[0]}")
    print(f"Best action: {min_tile} with {min_bombs} bombs")

    
    # Return action location, rClick, and probability of success
    return min_tile, False, probability
                            
# Helper function of chooseBestAction()
# Checks every possible layout of bombs on tiles adjacent to number tiles
def checkAllLayouts(game_matrix, bomb_matrix, up_tiles, old_bomb_set, board_width, board_height, valid_arrangements):
    # Create copy of bomb_set to not modify the original
    bomb_set = set()
    if old_bomb_set is not None:
        bomb_set = old_bomb_set.copy()
    
    # For every element in up_tiles set
    if len(up_tiles) != 0:
        tile = next(iter(up_tiles))
        remaining_up_tiles = up_tiles.copy()
        remaining_up_tiles.remove(tile)
        
        bomb_set_with_tile = bomb_set.copy()
        bomb_set_with_tile.add(tile)
        if len(up_tiles) != 0:
            print(f"Recursing with {len(up_tiles)} tiles...")
            
        # Check if tile layout is consistent / valid
        if not isConsistent(game_matrix, bomb_set_with_tile, board_width, board_height):
            return  # prune this branch
        
        # Set popped tile as either bomb (add to bomb_set) or free tile (don't add), recursively call through all elements
        checkAllLayouts(game_matrix, bomb_matrix, remaining_up_tiles, bomb_set_with_tile, board_width, board_height, valid_arrangements)
        checkAllLayouts(game_matrix, bomb_matrix, remaining_up_tiles, bomb_set, board_width, board_height, valid_arrangements)
        
    # Once all elements have been iterated through, check if configuration is valid based on number tiles
    else:
        # Iterate through all number tiles
        for y in range(board_height):
            for x in range(board_width):
                if game_matrix[y][x] != None and game_matrix[y][x] != -1:
                    # Count for all adjacent bombs to number tile
                    bombs = 0
                    
                    # Check all adjacent tiles
                    for j in range(-1, 2):
                        for i in range(-1, 2):
                            # Bounds check
                            if y + j < 0 or y + j >= board_height or x + i < 0 or x + i >= board_width:
                                continue
                            
                            # Don't check number tile
                            if j != 0 or i != 0:
                                # If tile is a flag, increment bombs count
                                if game_matrix[y + j][x + i] == -1:
                                    bombs += 1
                                    
                                # If tile is in bomb_set, increment bombs count
                                elif (x + i, y + j) in bomb_set:
                                    bombs += 1
                                    
                                # If tile is not a flag
                                if game_matrix[y + j][x + i] != -1:
                                    # Change None to 0 in bomb_matrix since to add tile as possible action
                                    if game_matrix[y + j][x + i] is None:
                                        if bomb_matrix[y + j][x + i] is None:
                                            bomb_matrix[y + j][x + i] = 0
                
                    # If the number of bombs does not equal the tile number, arrangement is invalid
                    if bombs != game_matrix[y][x]:
                        return
                    
        # If every tile had a valid arrangement, add arrangement to bomb_matrix
        while len(bomb_set) != 0:
            # Get bomb coordinate
            x, y = bomb_set.pop()
            # Increment value at gotten location
            if bomb_matrix[y][x] is None:
                bomb_matrix[y][x] = 1
            else:
                bomb_matrix[y][x] += 1
        
        # Also increment valid_arrangements
        valid_arrangements[0] += 1
    
# Helper function for checkAllLayouts
# Checks if a layout around a specific number tile is valid
# Return values:
# True:     Layout is consistent
# False:    Layout is not consistent
def isConsistent(game_matrix, bomb_set, board_width, board_height):
    for y in range(board_height):
        for x in range(board_width):
            if game_matrix[y][x] is not None and game_matrix[y][x] != -1:
                bombs = 0
                unknowns = 0

                for j in range(-1, 2):
                    for i in range(-1, 2):
                        nx, ny = x + i, y + j
                        if 0 <= nx < board_width and 0 <= ny < board_height and (i != 0 or j != 0):
                            if game_matrix[ny][nx] == -1 or (nx, ny) in bomb_set:
                                bombs += 1
                            elif game_matrix[ny][nx] is None and (nx, ny) not in bomb_set:
                                unknowns += 1

                number = game_matrix[y][x]
                
                # Prune if too many bombs already placed, or too few left to reach number
                if bombs > number:
                    return False
                if bombs + unknowns < number:
                    return False
    return True

# Gets the current state of the game board ie where the numbers are, and sets them to the inputted game_matrix
# Return values:
# 0: Success
# 1: Failed to scan on third attempt; game likely didn't update
# 2: Function dropped off bottom which should never happen
def getGameState(game_matrix, board_width, board_height, tile_coord, tile_width):
    # Loop to allow for retries in case board has not yet been updated since last scan
    # Ideally the loop's contents should only execute once
    for tries in range(3):
        screenshot = pyautogui.screenshot()
        x = y = 0
        temp_matrix = copy.deepcopy(game_matrix)
        
        # Scan each tile
        for y in range(board_height):
            for x in range(board_width):
                # Only need to check tile if it was previously up
                if temp_matrix[y][x] != None:
                    # Tile already down
                    continue
                
                # Check if tile is still up
                if screenshot.getpixel(((tile_coord[0] + x * tile_width), (tile_coord[1] + y * tile_width))) == BACKGROUNDCOLOR:
                    continue
                
                # Scan across x of tile (middle of y) for a valid color
                scannedColors = []
                matchFailed = True
                for i in range(int(tile_width / 4), tile_width - int(tile_width / 4)):
                    pixelColor = screenshot.getpixel(((tile_coord[0] + x * tile_width + i), (tile_coord[1] + (y * tile_width) + (tile_width / 2))))
                    scannedColors.append(pixelColor)
                    
                    # Decipher color to number on tile
                    match scannedColors[i - int(tile_width / 4)]:
                        # Blue
                        case (0, 0, 255):
                            # Number 1
                            temp_matrix[y][x] = 1
                            matchFailed = False
                            break
                        # Green
                        case (0, 123, 0):
                            # Number 2
                            temp_matrix[y][x] = 2
                            matchFailed = False
                            break
                        # Red
                        case (255, 0, 0):
                            # Number 3
                            temp_matrix[y][x] = 3
                            matchFailed = False
                            break
                        # Dark blue
                        case (0, 0, 123):
                            # Number 4
                            temp_matrix[y][x] = 4
                            matchFailed = False
                            break
                        # Dark red
                        case (123, 0, 0):
                            # Number 5
                            temp_matrix[y][x] = 5
                            matchFailed = False
                            break
                        # Cyan
                        case (0, 123, 123):
                            # Number 6
                            temp_matrix[y][x] = 6
                            matchFailed = False
                            break
                        # Black
                        case (0, 0, 0):
                            # Number 7
                            temp_matrix[y][x] = 7
                            matchFailed = False
                            break
                        # Gray
                        case (123, 123, 123):
                            # Number 8
                            temp_matrix[y][x] = 8
                            matchFailed = False
                            break
                        # Background color
                        case (189, 189, 189):
                            # Do nothing
                            continue
                        # Unknown color detected which is a bug if happens
                        case _:
                            # Print scanned colors for debuggin and exit
                            print("Colors scanned:", scannedColors)
                            raise RuntimeError("Unknown color detected during getGameState(). Colors scanned: " + str(scannedColors))
                
                # If no other number could be detected based on the colors scanned it's 0
                if matchFailed:
                    # Number 0
                    temp_matrix[y][x] = 0
                    
        # Check if the board is unchanged from last scan
        if temp_matrix == game_matrix:
            # Matrix is unchanged, check number of attempts
            if tries == 0:
                # If first attempt, retry scan
                continue
            elif tries == 1:
                # Second attempt, wait 1 second and then retry to give game time to update
                time.sleep(1)
                continue
            else:
                # Third attempt, give up on scan and return 1
                print("getGameState: Failed to scan")
                return 1
        else:
            # The board is different and scan was successful, update game_matrix and return
            for i in range(len(temp_matrix)):
                for j in range(len(temp_matrix[0])):
                    game_matrix[i][j] = temp_matrix[i][j]
            
            return 0
    
    # Failsafe, return 2
    print("getGameState: Dropped off bottom")
    return 2                

# Clicks a selected tile from its matrix coordinates (pos[0], pos[1])
# and left clicks if rClick is false, otherwise right clicks
# Return values:
# 0 on success
# 1 on faliure when inputted pos is not a valid tile
def clickTile(pos, rClick, board_width, board_height, tile_coord, tile_width):
    x, y = pos
    
    # Check if coordinates are within tile bounds
    if x < 0 or x >= board_width or y < 0 or y >= board_height:
        # Out of bounds
        return 1
    
    # Move to the center of the tile
    pyautogui.moveTo((tile_coord[0] + (x * tile_width) + (tile_width / 2)), (tile_coord[1] + (y * tile_width) + (tile_width / 2)))
    
    # Click button depending on rClick
    if rClick:  # Right click
        pyautogui.rightClick()
    else:       # Left click
        pyautogui.click()
    
    return 0

# Determines the how many tiles make up the width and height of the game board
# Return values:
# int width     : The number of tiles on the board horizontally
# int height    : The number of tiles on the board vertically
def getBoardSize(tile_coord, tile_width):
    x, y = tile_coord
    screenshot = pyautogui.screenshot()
    
    width = height = 0
    
    # Calculate width
    while screenshot.getpixel((x + tile_width - 1, y)) == TARGETCOLOR or screenshot.getpixel((x + tile_width - 1, y)) == TARGETBACK:
        x += tile_width
        width += 1
    
    # Calculate height
    x = tile_coord[0]
    while screenshot.getpixel((x, y + tile_width - 1)) == TARGETCOLOR or screenshot.getpixel((x, y + tile_width - 1)) == TARGETBACK:
        y += tile_width
        height += 1
    
    return width, height

# Returns the top left corner of the first tile:    tuple tile_coord = (int x, int y)
# and the width/height of each tile:                int width
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
# Return values:
# tuple (int x, int y)  : the pixel coordinates of the top left corner of the game
# None                  : when the target cannot be found
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