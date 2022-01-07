import time
import json
import os

from src.utils import *
from src.notify import send_message

import numpy as np
from PIL import Image
import nxbt

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

def saveArrayImage(array, filename):
    array = array.swapaxes(0,1) 
    as_image = pygame.pixelcopy.make_surface(array)
    filename = 'screenshots/' + filename + '.png'
    pygame.image.save(as_image, filename)

def moveTo(dst, nx, controller_index):
    curr = get_box_coords()
    print(curr)
    while(get_box_coords()[0] != dst[0]):
        if get_box_coords()[0] < dst[0]:
            nx.press_buttons(controller_index, [nxbt.Buttons.DPAD_RIGHT], up=1.0)
        else:
            nx.press_buttons(controller_index, [nxbt.Buttons.DPAD_LEFT], up=1.0)
    while(get_box_coords()[1] != dst[1]):
        curr = get_box_coords()
        print("Adjusting row -- current: " + str(curr) + " DST: " + str(dst[1]))
        if curr[1] < dst[1]:
            nx.press_buttons(controller_index, [nxbt.Buttons.DPAD_DOWN], up=1.0)
        else:
            nx.press_buttons(controller_index, [nxbt.Buttons.DPAD_UP], up=1.0)

def masuda():
    stats = None
    if os.path.isfile("stats.json"):
        with open("stats.json", "r") as f:
            stats = json.load(f)
    else:
        stats = {
            "reset_count": 0,
            "issues": 0,
            "log": []
        }

    menu_open_check = np.array(Image.open("./check-imgs/menu_open.png"))
    pokemon_menu_check = np.array(Image.open("./check-imgs/pokemon_menu_check.png"))
    box_view_check = np.array(Image.open("./check-imgs/box_view_check.png"))
    multiselect_check = np.array(Image.open("./check-imgs/multiselect_ref.png"))

    # Initialize an emulated controller and connect
    # to an available Switch.
    nx = nxbt.Nxbt()
    controller_index = nx.create_controller(
        nxbt.PRO_CONTROLLER,
        reconnect_address=nx.get_switch_addresses())
    nx.wait_for_connection(controller_index)

    add_to_stat_log(stats, "Controller Connected")

    time.sleep(5)

#    # take and save ref screenshots of hands, these dimensions should stay the same as call in getBoxPos()
#    # outdated, but I might still use later on...

#    OFFSET_X = 52
#    OFFSET_Y = 62
#
#    for i in range(6):
#        for j in range(6):
#            saveArrayImage(get_image()[95+(OFFSET_Y*i):99+(OFFSET_Y*i), 202+(OFFSET_X*j):208+(OFFSET_X*j), :],  str(j) + "_" + str(i))
#            print("Saved " + str(j) + "_" + str(i) + ".png")
#            if (j < 5):
#               nx.press_buttons(controller_index, [nxbt.Buttons.DPAD_RIGHT], up=2.0)
#            else:
#                nx.press_buttons(controller_index, [nxbt.Buttons.DPAD_DOWN], up=2.0)
#                for j in range(5):
#                    nx.press_buttons(controller_index, [nxbt.Buttons.DPAD_LEFT], up=2.0)
#    return
##    for i in range(5):
##        saveArrayImage(get_image()[87+(61*i):94+(61*i), 35:42, :], "-1_" + str(i))
##        nx.press_buttons(controller_index, [nxbt.Buttons.DPAD_DOWN], up=2.0)
#
#

    # press X until in menu 
    menu_view = False
    while (menu_view == False):
        nx.press_buttons(controller_index, [nxbt.Buttons.X], up=1.0)
        img = get_image()
        img_mse = mse(menu_open_check, img)
        add_to_stat_log(stats, f"Menu check MSE: {img_mse}")
        if img_mse < 51:
            menu_view = True
            break

    # press A until in pokemon party
    pokemon_view = False
    while (pokemon_view == False):
        nx.press_buttons(controller_index, [nxbt.Buttons.A], up=1.0)
        img = relative_crop(get_image(), .975, 1.0, .025, 0.0)
        img_mse = mse(pokemon_menu_check, img)
        add_to_stat_log(stats, f"Pokemon view check MSE: {img_mse}")
        if img_mse < 50:
            pokemon_view = True
            break

    # press R until in box
    box_view = False
    while (box_view == False):
        nx.press_buttons(controller_index, [nxbt.Buttons.R], up=1.0)
        img = get_image()[38:56, 0:18, :]
        img_mse = mse(box_view_check, img)
        add_to_stat_log(stats, f"Box view check MSE: {img_mse}")
        if img_mse < 50:
            box_view = True
            break

    # press Y until multiselect is enabled
    multiselect = False
    while (multiselect == False):
        nx.press_buttons(controller_index, [nxbt.Buttons.Y], up=1.0)
        img = get_image()[0:28, 115:143, :]
        img_mse = mse(multiselect_check, img)
        add_to_stat_log(stats, f"Multiselect check MSE: {img_mse}")
        if img_mse < 50:
            box_view = True
            break

    # Move to first pokemon in party
    moveTo((-1,1), nx, controller_index)

    # Select first pokemon
    nx.press_buttons(controller_index, [nxbt.Buttons.A], up=2.0)
    saveArrayImage(get_image(), "oneselected")
    moveTo((-1,5), nx, controller_index)
    nx.press_buttons(controller_index, [nxbt.Buttons.A], up=2.0)
    saveArrayImage(get_image(), "pickedup")
    moveTo((0,0), nx, controller_index)
    nx.press_buttons(controller_index, [nx.Buttons.A])


    

if __name__ == "__main__":
    masuda()
    print("Done")
#    send_message("Completed")

