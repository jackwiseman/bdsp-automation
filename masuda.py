import time
import json
import os

from src.utils import *
from src.notify import send_message

import numpy as np
from PIL import Image
import nxbt

def saveArrayImage(array, filename):
    as_image = pygame.pixelcopy.make_surface(array)
    filename = 'screenshots/' + filename + '.png'
    pygame.image.save(as_image, filename)

def get_box_coords(debug=False):
    hand_check = np.array(Image.open("./check-imgs/hand_ref.png"))
    img = get_image()
    OFFSET_X = 52
    OFFSET_Y = 62
    pos = (0,0)
    smallest = 200.0 # start with a large "small" value to ensure there will be a smaller one

    # check the party first, as this can save calculations
    for i in range(5):
        party = img[87+(61*i):94+(61*i), 35:42, :]
        if(party.mean() < 175.0):
            return (-1, i)
 
    # iterate over the box, checking for the largest amount of white space
    # requires "Simple" wallpaper and multiselect on
    for col in range(6):
        for row in range(5):
            candidate = img[95+(OFFSET_Y*row):101+(OFFSET_Y*row), 199+(OFFSET_X*col):208+(OFFSET_X*col), :] 
            #avg = candidate.mean()
            img_mse = mse(hand_check, candidate)
            if(debug):
                saveArrayImage(candidate, str(col) + "_" + str(row))
            print("(" + str(col) + ", " + str(row) + ") - " + str(img_mse))
            if(img_mse < smallest):
                smallest = img_mse 
                pos = (col, row)
    print("Best from this search: " + str(smallest) + " " + str(pos))
    return pos

def moveTo(dst, nx, controller_index):
    print("hi")
    curr = get_box_coords()
    print(curr)
    while(get_box_coords()[0] != dst[0]):
        curr = get_box_coords()
        print("Adjusting col -- current: " + str(curr[0]) + " DST: " + str(dst[0]))
        if curr[0] < dst[0]:
            nx.press_buttons(controller_index, [nxbt.Buttons.DPAD_RIGHT], up=1.0)
        else:
            nx.press_buttons(controller_index, [nxbt.Buttons.DPAD_LEFT], up=1.0)
    while(get_box_coords()[1] != dst[1]):
        curr = get_box_coords()
        print("Adjusting row -- current: " + str(curr[1]) + " DST: " + str(dst[1]))
        if curr[1] < dst[1]:
            nx.press_buttons(controller_index, [nxbt.Buttons.DPAD_DOWN], up=1.0)
        else:
            nx.press_buttons(controller_index, [nxbt.Buttons.DPAD_UP], up=1.0)

def reset_hunt():
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
    
    time.sleep(4)

#    print(get_box_coords())
    moveTo((4,4), nx, controller_index)

    a = True
    if a:
        return


    # press X until in menu 
    menu_view = False
    while (menu_view == False):
        nx.press_buttons(controller_index, [nxbt.Buttons.X], up=5.0)
        img = get_image()
        img_mse = mse(menu_open_check, img)
        add_to_stat_log(stats, f"Menu check MSE: {img_mse}")
        if img_mse < 50:
            menu_view = True
            break

    # press A until in pokemon party
    pokemon_view = False
    while (pokemon_view == False):
        nx.press_buttons(controller_index, [nxbt.Buttons.A], up=5.0)
        img = relative_crop(get_image(), .975, 1.0, .025, 0.0)
        img_mse = mse(pokemon_menu_check, img)
        add_to_stat_log(stats, f"Pokemon view check MSE: {img_mse}")
        if img_mse < 50:
            pokemon_view = True
            break

    # press R until in box
    box_view = False
    while (box_view == False):
        nx.press_buttons(controller_index, [nxbt.Buttons.R], up=5.0)
        img = get_image()[38:56, 0:18, :]
        img_mse = mse(box_view_check, img)
        add_to_stat_log(stats, f"Box view check MSE: {img_mse}")
        if img_mse < 50:
            box_view = True
            break

    # press Y until multiselect is enabled
    multiselect = False
    while (multiselect == False):
        nx.press_buttons(controller_index, [nxbt.Buttons.Y], up = 5.0)
        img = get_image()[0:28, 115:143, :]
        img_mse = mse(multiselect_check, img)
        add_to_stat_log(stats, f"Multiselect check MSE: {img_mse}")
        if img_mse < 50:
            box_view = True
            break

    # test movement
    moveTo((5,4), nx, controller_index)

if __name__ == "__main__":
    reset_hunt()
    send_message("Completed")
