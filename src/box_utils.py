import numpy as np
from PIL import Image
import nxbt # necessary?
from src.utils import *

## assumed menu configuration (default) -- I think?
# [pokedex ] [   pokemon   ] [  bag  ] [trainer card]
# [town map] [ball capsules] [options] [mystery gift]
def open_menu(nx, controller_index, town_map=False, pokemon=False, debug=False):
    menu_open_check = np.array(Image.open("./check-imgs/menu_open.png")) # TODO - this should be updated, selection includes entire screen

    MENU_TOLERANCE = 65 # color
    TOWN_MAP_TOLERANCE = 215 # based on white
    POKEMON_TOLERANCE = 160 # based on white

    # Press X until menu is open
    if debug:
        print("Opening menu")
    menu_view = False
    while (menu_view == False):
        nx.press_buttons(controller_index, [nxbt.Buttons.X], up=1.0)
        img = get_image()
        img_mse = mse(menu_open_check, img)
        if(debug):
            print(f"Menu check MSE: {img_mse} Tolerance: {MENU_TOLERANCE}")
        if img_mse < MENU_TOLERANCE:
            menu_view = True
            break

    if town_map == pokemon:
        if debug:
            print("Nothing selected, returning")
        return

    # init
    img = get_image() # arbitrary
    tolerance = 0

    if town_map == True:
        tolerance = TOWN_MAP_TOLERANCE
    elif pokemon == True:
        tolerance = POKEMON_TOLERANCE

    selected = False
    while(not(selected)):
        for i in range(4): # alternate between rows of icons
            if town_map == True:
                img = np.dot(get_image()[186:192, 143:149][...,:3], [.3, .6, .1])
            elif pokemon == True:
                img = np.dot(get_image()[68:78, 262:272][...,:3], [.3, .6, .1])
            m = img.max()
            print(f"Menu check max: {m} Tolerance: {tolerance}")
            if(img.max() > tolerance):
                selected = True
                break
            else:
                nx.press_buttons(controller_index, [nxbt.Buttons.DPAD_RIGHT], up=1.0)
        if not(selected):
            nx.press_buttons(controller_index, [nxbt.Buttons.DPAD_DOWN], up=1.0)

# Open view to the box from the game view with a specified select mode (single select by default)
def open_box(nx, controller_index, multiselect=False, debug=False):
    box_view_check = np.array(Image.open("./check-imgs/box_view_check.png"))
    multiselect_check = np.array(Image.open("./check-imgs/multiselect_ref.png"))
    pokemon_menu_check = np.array(Image.open("./check-imgs/pokemon_menu_check.png"))

    open_menu(nx, controller_index, pokemon=True, debug=debug)

    # press A until in pokemon party
    pokemon_view = False
    while (pokemon_view == False):
        nx.press_buttons(controller_index, [nxbt.Buttons.A], up=1.0)
        img = relative_crop(get_image(), .975, 1.0, .025, 0.0)
        img_mse = mse(pokemon_menu_check, img)
        if debug:
            print(f"Pokemon view check MSE: {img_mse}")
        if img_mse < 50:
            pokemon_view = True
            break

    # press R until in box
    box_view = False
    while (box_view == False):
        nx.press_buttons(controller_index, [nxbt.Buttons.R], up=1.0)
        img = get_image()[38:56, 0:18, :]
        img_mse = mse(box_view_check, img)
        if debug:
            print(f"Box view check MSE: {img_mse}")
        if img_mse < 50:
            box_view = True
            break

    if multiselect == False:
        return

    # press Y until multiselect is enabled
    multiselect = False
    while (multiselect == False):
        nx.press_buttons(controller_index, [nxbt.Buttons.Y], up=1.0)
        img = get_image()[0:28, 115:143, :]
        img_mse = mse(multiselect_check, img)
        if debug:
            add_to_stat_log(f"Multiselect check MSE: {img_mse}")
        if img_mse < 50:
            box_view = True
            break

# find the position of the cursor in the box by taking a screenshot, converting it
# to greyscale and checking predetermined slices where the cursor can show up, finding
# the slice which contains the pixel closest to white
def get_box_coords(debug=False):
    img = get_image()
    img = np.dot(img[...,:3], [.3, .6, .1]) # convert to greyscale

    OFFSET_X = 52 # step size in x direction
    OFFSET_Y = 62 # step size in y direction
    pos = (0,0)
    largest = 0.0 # ensure a result will be found

    # check the party first
    for row in range(6):
        party = img[89+(61*row):94+(61*row), 35:42]
        if(debug):
            print("(-1, " + str(row) + ") - " + str(party.max()))
        if(party.max() > largest):
            largest = party.max()
            pos = (-1, row)
 
    # iterate over the box
    # requires "Simple" wallpaper and multiselect on
    for col in range(6):
        for row in range(5):
            candidate = img[95+(OFFSET_Y*row):99+(OFFSET_Y*row), 202+(OFFSET_X*col):208+(OFFSET_X*col)] 
            if(debug):
                print("(" + str(col) + ", " + str(row) + ") - " + str(candidate.max()))
            if(candidate.max() > largest):
                largest = candidate.max()
                pos = (col, row)
    return pos

# return an array of all positions that are currently highlighted using multiselect
# done by checking a small area above each icon and testing the green values to see
# if they are greater than a threshold
def get_selected_coords(debug=False):
    img = get_image()
    OFFSET_X = 52 # step size in x direction
    OFFSET_Y = 62 # step size in y direction
    threshold_box = 239.0 # THIS HAS BEEN RECENTLY CHANGED FROM 240
    threshold_party = 200.0
    selected = []

    # check party
    for row in range(6):
        candidate = img[122+(OFFSET_Y*row):129+(OFFSET_Y*row), 143:150] 
        max_green_val = candidate[ :, :, 1].max()
        if(debug):
            print(f"(-1, {row}): {max_green_val}")
        if max_green_val > threshold_party:
            selected.append((-1, row))

    # check box
    for col in range(6): #these may need to be switched in order to get first appearance
        for row in range(5):
            candidate = img[109+(OFFSET_Y*row):111+(OFFSET_Y*row), 194+(OFFSET_X*col):197+(OFFSET_X*col)] 
            max_green_val = candidate[ :, :, 1].max()
            if(debug):
                #save_array_as_image(candidate, f"{row}")
                print(f"({col}, {row}): {max_green_val}")
            if max_green_val > threshold_box:
                selected.append((col, row))
    return selected

# Find the position of the picked up pokemon by converting the image to greyscale, parsing predetermined slices
# of the screenshot and returning the first slice to surpass the white threshold, false if none are found
def get_picked_up_coords(debug=False):
    img = get_image()
    img = np.dot(img[...,:3], [.3, .6, .1]) # convert to greyscale
    box_selection = [192, 196, 96, 100] # base box crop, not sure if I want to keep this, but reduces magic numbers below
    party_selection = [20, 24, 80, 82]
    OFFSET_X = 52 # step size in x direction
    OFFSET_Y = 62 # step size in y direction
    box_threshold = 230
    party_threshold = 213

    # check party
    for row in range(6):
        candidate = img[party_selection[2]+(OFFSET_Y*row):party_selection[3]+(OFFSET_Y*row), party_selection[0]:party_selection[1]]
        max_white = candidate.max()
        if(debug):
            print(f"(-1, {row}: {max_white})")
        if(max_white > party_threshold):
            return (-1, row)

    # check box
    for row in range(5): # row goes first so that we can return the FIRST instance of > white threshold
        for col in range(6):
            candidate = img[box_selection[2]+(OFFSET_Y*row):box_selection[3]+(OFFSET_Y*row), box_selection[0]+(OFFSET_X*col):box_selection[1]+(OFFSET_X*col)]
            max_white = candidate.max()
            if(debug):
                print(f"({col}, {row}: {max_white}")
            if(max_white > box_threshold):
                return (col, row)
    return False


def move_to(dst, nx, controller_index, picked_up=False):
    if(picked_up == False):
        while(get_box_coords()[0] != dst[0]):
            if get_box_coords()[0] < dst[0]:
                nx.press_buttons(controller_index, [nxbt.Buttons.DPAD_RIGHT], up=1.0)
            else:
                nx.press_buttons(controller_index, [nxbt.Buttons.DPAD_LEFT], up=1.0)
        while(get_box_coords()[1] != dst[1]):
            if get_box_coords()[1] < dst[1]:
                nx.press_buttons(controller_index, [nxbt.Buttons.DPAD_DOWN], up=1.0)
            else:
                nx.press_buttons(controller_index, [nxbt.Buttons.DPAD_UP], up=1.0)
    else:
        while(get_picked_up_coords(debug=True)[0] != dst[0]):
            if get_picked_up_coords()[0] < dst[0]:
                nx.press_buttons(controller_index, [nxbt.Buttons.DPAD_RIGHT], up=1.0)
            else:
                nx.press_buttons(controller_index, [nxbt.Buttons.DPAD_LEFT], up=1.0)
        while(get_picked_up_coords(debug=True)[1] != dst[1]):
            if get_picked_up_coords()[1] < dst[1]:
                nx.press_buttons(controller_index, [nxbt.Buttons.DPAD_DOWN], up=1.0)
            else:
                nx.press_buttons(controller_index, [nxbt.Buttons.DPAD_UP], up=1.0)

# Return True if (col, row) is selectd, False otherwise
def is_selected(coord):
    return coord in get_selected_coords()

# move box view to first page available, by searching for the "bookend" and moving one page before it
def first_page(nx, controller_index, bookend_page=False):
    bookend_check = np.array(Image.open("./check-imgs/bookend.png"))
    print("Looking for bookend")

    found_bookend = False
    while(found_bookend == False):
        nx.press_buttons(controller_index, [nxbt.Buttons.L], up=2.0)
        img = get_image()[124:132,205:213]
        img_mse = mse(bookend_check, img)
        print(img_mse)
        if img_mse < 80:
            found_bookend = True
            if bookend_page == True:
                return
            break

    while(found_bookend == True):
        nx.press_buttons(controller_index, [nxbt.Buttons.R], up=2.0)
        img = get_image()[124:132,205:213]
        img_mse = mse(bookend_check, img)
        print(img_mse)
        if img_mse > 80:
            found_bookend = False
            break
            
# move box view to last page available, by searching for the "bookend" and moving one page after it
def last_page(nx, controller_index):
    bookend_check = np.array(Image.open("./check-imgs/bookend.png"))

    found_bookend = False
    while(found_bookend == False):
        nx.press_buttons(controller_index, [nxbt.Buttons.R], up=2.0)
        img = get_image()[124:132,205:213]
        img_mse = mse(bookend_check, img)
        print(img_mse)
        if img_mse < 80:
            found_bookend = True
            break

    while(found_bookend == True):
        nx.press_buttons(controller_index, [nxbt.Buttons.L], up=2.0)
        img = get_image()[124:132,205:213]
        img_mse = mse(bookend_check, img)
        print(img_mse)
        if img_mse > 80:
            found_bookend = False
            break

# Move a column of pokemon in the box from (src, x) to (dst, x) -- makes an adjustment for party pokemon
def move_col(nx, controller_index, src_col, dst_col, check_for_shiny=False, debug=False):
    src = (src_col, 0)
    dst = (dst_col, 0)
    shiny_tol = 25
    
    # adjust for party
    if src_col == -1:
        src = (src_col, src[1] + 1)
    if dst_col == -1:
        dst = (dst_col, dst[1] + 1)

    # Move to first pos
    move_to(src, nx, controller_index)

    # Select first pokemon
    while(is_selected(src) == False):
        nx.press_buttons(controller_index, [nxbt.Buttons.A], up=2.0)

    # Select col 
    if check_for_shiny == False:
        while(is_selected((src[0], src[1]+4)) == False):
            move_to((src[0], src[1]+4), nx, controller_index)
    else:
        shiny_ref = np.array(Image.open("./check-imgs/shiny_indicator.png"))
        while(is_selected((src[0], src[1]+4)) == False):
            img = get_image()[71:94, 692:715]
            img_mse = mse(img, shiny_ref)
            if debug:
                print(f"Shiny MSE: {img_mse}")
            if img_mse < shiny_tol:
                print("no way")
                return True
            for i in range(src[1], src[1]+5):
                move_to((src[0], i), nx, controller_index)
                img = get_image()[71:94, 692:715]
                img_mse = mse(img, shiny_ref)
                if debug:
                    print(f"Shiny MSE: {img_mse}")
                if img_mse < 20:
                    print("no way")
                    return True # shiny found

    # Pick up 
    while(get_picked_up_coords() == False):
        nx.press_buttons(controller_index, [nxbt.Buttons.A], up=2.0)

    # Move to dst
    move_to(dst, nx, controller_index, picked_up=True)
    
    # Place
    while(get_picked_up_coords() != False):
        nx.press_buttons(controller_index, [nxbt.Buttons.A], up=2.0)




