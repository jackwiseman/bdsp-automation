import time
import json
import os
import sys

from src.utils import *
from src.notify import send_message
from src.box_utils import *
from datetime import datetime

import numpy as np
from PIL import Image
import nxbt


def move_to_nursery_man(nx, controller_index, debug=False):
    corner_1_ref = []
    corner_2_ref = []
    inline_ref = []
    
    # tolerances
    corner_1_tol = 50
    corner_2_tol = 50
    inline_tol = 50

    # load all reference images
    for i in range(len(os.listdir("./check-imgs/nursery-man/corner-1/"))):
        corner_1_ref.append(np.array(Image.open("./check-imgs/nursery-man/corner-1/" + str(i + 1) + ".png")))
    for i in range(len(os.listdir("./check-imgs/nursery-man/corner-2/"))):
        corner_2_ref.append(np.array(Image.open("./check-imgs/nursery-man/corner-2/" + str(i + 1) + ".png")))
    for i in range(len(os.listdir("./check-imgs/nursery-man/inline/"))):
        inline_ref.append(np.array(Image.open("./check-imgs/nursery-man/inline/" + str(i + 1) + ".png")))

    open_menu(nx, controller_index, town_map=True)

    # Select and fly
    for i in range(7):
        nx.press_buttons(controller_index, [nxbt.Buttons.A], up=1.0)

    # Move to corner of fence
    if debug:
        print("-- Moving to bottom corner of fence --")
    reached_first_corner = False

    timeout = 11
    while(reached_first_corner == False):
        nx.press_buttons(controller_index, [nxbt.Buttons.DPAD_LEFT], up=1.0)
        img = get_image()[198:237, 294:323]
        img_mse = 1000 # arbitrary large num
        for i in corner_1_ref:
            img_mse = min(mse(i, img), img_mse)
        if debug:
            print(f"MSE: {img_mse} TOL: {corner_1_tol} Timeout: {timeout}")
        if img_mse < corner_1_tol:
            reached_first_corner = True
            break
        if timeout == 0 and not(reached_first_corner):
            time_as_string = str(datetime.now().time())
            save_array_as_image(img, f"corner_1_update_{time_as_string}") # save potential ref
            return False
        timeout -= 1

    # Go to top of fence
    reached_second_corner = False
    timeout = 7 # number of steps
    while(reached_second_corner == False):
        nx.press_buttons(controller_index, [nxbt.Buttons.DPAD_UP], up=1.0)
        img = get_image()[248:279, 286:317]
        img_mse = 1000 # arbitrary large num
        for i in corner_2_ref:
            img_mse = min(mse(i, img), img_mse)
        if debug:
            print(f"MSE: {img_mse} TOL: {corner_2_tol} Timeout: {timeout}")
        if img_mse < corner_2_tol:
            reached_second_corner = True
            break
        if timeout == 0 and not(reached_second_corner):
            time_as_string = str(datetime.now().time())
            save_array_as_image(img, f"corner_2_update_{time_as_string}") # save potential ref
            return False
        timeout -= 1


    # no need to check images here, just spam the dpad_left to make sure we're against the left fence, although checking will probably speed it up
    nx.press_buttons(controller_index, [nxbt.Buttons.DPAD_LEFT], down=2.0)

    # move so that we're in the same line as the old man
    if debug:
        print("-- Attempting to line up with nursery man --")
    inline = False
    timeout = 2 # number of steps
    while(inline == False):
        nx.press_buttons(controller_index, [nxbt.Buttons.DPAD_UP], up=1.0)
        img = get_image()[168:203, 404:439]
        img_mse = 1000 # arbitrary large num
        for i in inline_ref:
            img_mse = min(mse(i, img), img_mse)
        if debug:
            print(f"MSE: {img_mse} TOL: {inline_tol} Timeout: {timeout}")
        if img_mse < inline_tol:
            inline = True
            break
        if timeout == 0 and not(inline):
            time_as_string = str(datetime.now().time())
            save_array_as_image(img, f"inline_ref_update_{time_as_string}") # save potential ref
            return False
        timeout -= 1
    timeout = 3
    return True

def move_to_bike_path(nx, controller_index, debug=False):
    ref = []
    # load all reference images
    for i in range(len(os.listdir("./check-imgs/bike-path/"))):
        ref.append(np.array(Image.open("./check-imgs/bike-path/" + str(i + 1) + ".png")))
        print("Added " + str(i + 1) + ".png")

    open_menu(nx, controller_index, town_map=True)

    # spam A to fly to Solaceon town (assumes we're already here)
    for i in range(10):
        nx.press_buttons(controller_index, [nxbt.Buttons.A], up=1.0)

    # close the poketech
    nx.press_buttons(controller_index, [nxbt.Buttons.R], down=1.0, up=0.2)

    img = get_image()[137:172, 501:536]
    timeout = 4
    on_bike_path = False
    while (on_bike_path == False):
        nx.press_buttons(controller_index, [nxbt.Buttons.DPAD_LEFT], up=1.0)
        img = get_image()[137:172, 501:536]
        img_mse = 1000 # arbitrary large num
        if debug:
            print("Testing 4 vals:")
        for i in ref:
            img_mse = min(mse(i, img), img_mse)
            if debug:
                print(img_mse)
        if img_mse < 30:
            on_bike_path = True
            break
        if timeout == 0 and not(on_bike_path): 
            time_as_string = str(datetime.now().time())
            save_array_as_image(img, f"bikepath_ref_update_{time_as_string}") # save potential ref
            return False
        timeout -= 1
    return True

def init_bookends():
    img = get_image()[124:132, 205:213]
    array = img.swapaxes(0,1) 
    as_image = pygame.pixelcopy.make_surface(array)
    filename = 'check-imgs/bookend.png'
    pygame.image.save(as_image, filename)
    

def init_breed_species():
    img = get_image()[124:132, 205:213]
    array = img.swapaxes(0,1) 
    as_image = pygame.pixelcopy.make_surface(array)
    filename = 'check-imgs/breedspecies.png'
    pygame.image.save(as_image, filename)

# requires two things registered, bike at bottom
def bike_toggle(nx, controller_index, debug=False):
    bike_check = np.array(Image.open("./check-imgs/bike-ref.png"))
    # Hop on the bike by first ensuring the registered menu is open and then checking to see if it has been closed (ie by pressing +)
    bike_view = False
    while (bike_view == False):
        img = get_image()[287:350, 330:393]
        save_array_as_image(img, "bikewtf")
        nx.press_buttons(controller_index, [nxbt.Buttons.PLUS], up=2.0)
        img_mse = mse(bike_check, img)
        if debug:
            print(f"Bike MSE: {img_mse}")
        if img_mse < 30:
            print("Bike menu opened")
            bike_view = True
            break

    while (bike_view == True):
        img = get_image()[287:350, 330:393]
        nx.press_buttons(controller_index, [nxbt.Buttons.DPAD_DOWN], up=1.0)
        img_mse = mse(bike_check, img)
        if img_mse > 50:
            bike_view = False
            break

def solaceon(nx, controller_index):
    # get on bike
    bike_toggle(nx, controller_index)

    # go to bottom of path
    nx.press_buttons(controller_index, [nxbt.Buttons.DPAD_DOWN], down=11.0)

    # go to middle of solaceon
    nx.press_buttons(controller_index, [nxbt.Buttons.DPAD_UP], down=5.2)

# assumes you are are standing to the left of the man
def get_new_eggs(num_eggs, nx, controller_index, stats, debug=False):
    egg_check = np.array(Image.open("./check-imgs/egg-ref.png"))
    man_talking_check = np.array(Image.open("./check-imgs/man_talking_check.png"))
    menu_open_check = np.array(Image.open("./check-imgs/menu_open.png"))
    eggs_received = 0
    egg_ready = False

    # first we need to prepare the party for receiving eggs by moving the "dummy" pokemon to the party

    open_box(nx, controller_index, multiselect=True)

    # go to box[-1]
    first_page(nx, controller_index, bookend_page=True)

    # Move dummy col to party
    move_col(nx, controller_index, 5, -1)

    # Go to last page before first page as first_page() moves right first before calculating TODO: check logic on that
    last_page(nx, controller_index)
    first_page(nx, controller_index)

    # Spam B until we get back to the game view
    for i in range(15):
        nx.press_buttons(controller_index, [nxbt.Buttons.B])
    
    # Now we're ready to get pokemon

    while(eggs_received < num_eggs):
        for i in range(4):
            nx.press_buttons(controller_index, [nxbt.Buttons.DPAD_LEFT], down=1.0, up=0.2)
            nx.press_buttons(controller_index, [nxbt.Buttons.DPAD_RIGHT], down=1.0, up=0.2)
        nx.press_buttons(controller_index, [nxbt.Buttons.DPAD_LEFT], down=1.0, up=0.2)
        for i in range(2):
            nx.press_buttons(controller_index, [nxbt.Buttons.R], down=1.0, up=0.2)
        img = get_image()[104:124,601:618]
        img_mse = mse(img, egg_check)
        if debug:
            print(f"Egg check MSE: {img_mse}, Tolerance = 50")
        if img_mse < 50: # this tolerance should be able to be lower...
            # egg found

            # move to the right twice to ensure we actually get to the man
            for i in range(2):
                nx.press_buttons(controller_index, [nxbt.Buttons.DPAD_RIGHT], down=1.0)
            if debug:
                print("spam A until the man asks if we want the egg")
            egg_confirmation = False
            while(egg_confirmation == False):
                nx.press_buttons(controller_index, [nxbt.Buttons.A], up=0.5)
                img = np.dot(get_image()[334:344,570:580][...,:3], [.3, .6, .1])
                if debug:
                    print(f"Max: {img.max()}, looking for > 200")
                if img.max() > 200: 
                    egg_confirmation = True
                    break

            if debug:
                print("spam A until the man asks us to take good care of it (ie pokemon nursery man title comes back up)")
            take_good_care = False
            while(take_good_care == False):
                nx.press_buttons(controller_index, [nxbt.Buttons.A], up=0.5)

                candidate = get_image()[365:384, 160:309]
                img_mse = mse(man_talking_check, candidate)
                if debug:
                    print(f"MSE (with tolerance 10): {img_mse}")
                if img_mse < 50 : 
                    take_good_care = True
                    break

            if(debug):
                print("spam A until this goes away, continue")
            while(take_good_care == True):
                nx.press_buttons(controller_index, [nxbt.Buttons.A], up=0.5)
                candidate = get_image()[365:384, 160:309]
                img_mse = mse(man_talking_check, candidate)
                if(debug):
                    print(f"MSE with tolerance 10: {img_mse}")
                if img_mse > 50:
                    take_good_care = False
                    break
            print("Received egg " + str(eggs_received + 1) + "/" + str(num_eggs))
            stats["eggs"] += 1
            with open("stats.json", "w") as f:
                json.dump(stats, f)
            eggs_received += 1
            continue

        else:
            nx.press_buttons(controller_index, [nxbt.Buttons.DPAD_RIGHT], down=1.0)

    # Finally, we undo what we did to start, by removing the dummy pokemon
    open_box(nx, controller_index, multiselect=True)

    # go to box[-1]
    first_page(nx, controller_index, bookend_page=True)

    # Move dummy col to party
    move_col(nx, controller_index, -1, 5)

    # Go to last page before first page as first_page() moves right first before calculating TODO: check logic on that
    last_page(nx, controller_index)
    first_page(nx, controller_index)
    
    # Place the first column of eggs in the party
    move_col(nx, controller_index, 0, -1)

    # Spam B until we get back to the game view
    for i in range(15):
        nx.press_buttons(controller_index, [nxbt.Buttons.B])
    
    # Now we're ready to hatch!



# intended to be used when all boxes are fully hatched, ie there are no eggs or empty spaces
# use with caution as this is mostly untested
# essentially a "reset"
def release_boxes(stats, nx, controller_index, debug=False): # add num_boxes arg
    box_menu_check = np.array(Image.open("./check-imgs/box_menu_check.png"))
    release_select_check = np.array(Image.open("./check-imgs/release_select_check.png"))
    release_confirmation_check = np.array(Image.open("./check-imgs/release_confirmation_check.png"))
    release_textbox_check = np.array(Image.open("./check-imgs/release_textbox_check.png"))
    breed_speecies_check = np.array(Image.open("./check-imgs/breedspecies.png"))
    bookend_check = np.array(Image.open("./check-imgs/bookend.png"))

    # open box
    open_box(nx, controller_index)

    # go to first page
    first_page(nx, controller_index)

    # move to next box with intended breed pokemon in slot (0,0)
    # TODO: reduce magic numbers, tie in img resolutions with init functions
    pokemon_at_0_pos = get_image()[124:132, 205:213]
    while mse(bookend_check, pokemon_at_0_pos) > 80: # while we haven't reached the end
        if mse(breed_speecies_check, pokemon_at_0_pos) > 10: # empty space found, skip this box
            print("skip!")
            nx.press_buttons(controller_index, [nxbt.Buttons.R],up=2.0)
            pokemon_at_0_pos = get_image()[124:132, 205:213] # update view
        else:
            print("gotta do something")
            for col in range(6):
                for row in range(5):
                    # can speed this up a few seconds by "snaking" around the box
                    move_to((col, row), nx, controller_index)

        #            # Decide if there's a pokemon here
        #
        #            img = get_image()[124+(62*row):132+(62*row), 205+(52*col):213+(52*col)]
        #            img_mse = mse(breed_speecies_check, img)
        #            print(f"({col}, {row}): {img_mse}")
        #            if img_mse > 120:
        #                print("There's no pokemon here!")
        #                continue

                    # Open the box action menu
                    if debug:
                        print("Open action menu")
                    box_menu_open = False
                    while(box_menu_open == False):
                        nx.press_buttons(controller_index, [nxbt.Buttons.A], up=1.2)
                        img = get_image()[200:374, 461:594]
                        img_mse = mse(box_menu_check, img)
                        if debug:
                            print(f"MSE: {img_mse}, TOL: 25")
                        if img_mse < 25:
                            box_menu_open = True
                            break
                    
                    # move arrow until 'release' is selected
                    if debug:
                        print("move arrow until 'release' is selected")
                    release_selected = False
                    while(release_selected == False):
                        nx.press_buttons(controller_index, [nxbt.Buttons.DPAD_DOWN], up=1.2)
                        img = get_image()[317:343, 463:477]
                        img_mse = mse(release_select_check, img)
                        if debug:
                            print(f"MSE: {img_mse}, TOL: 50")
                        if img_mse < 50:
                            release_selected = True
                            break

                    # press A until the arrow isn't seen anymore
                    if debug:
                        print("press A until the arrow isn't seen anymore")
                    while(release_selected == True):
                        nx.press_buttons(controller_index, [nxbt.Buttons.A], up=1.2)
                        img = get_image()[317:343, 463:477]
                        img_mse = mse(release_select_check, img)
                        if debug:
                            print(f"MSE: {img_mse}, TOL: 50")
                        if img_mse > 50:
                            release_selected = False
                            break

                    # move arrow until "Yes" confirmation is highlighted
                    if debug:
                        print("move arrow until 'Yes' confirmation is highlighted")
                    confirmation_selected = False
                    while(confirmation_selected == False):
                        nx.press_buttons(controller_index, [nxbt.Buttons.DPAD_UP], up=1.2)
                        img = get_image()[316:343, 462:479]
                        img_mse = mse(release_confirmation_check, img)
                        if debug:
                            print(f"MSE: {img_mse}, TOL: 40")
                        if img_mse < 45:
                            confirmation_selected = False
                            break

                    # press A until white text box is gone
                    if debug:
                        print("press A until white text box is gone")
                    released = False
                    while(released == False):
                        nx.press_buttons(controller_index, [nxbt.Buttons.A],up=1.2)
                        img = get_image()[446:460, 452:471]
                        img_mse = mse(release_textbox_check, img)
                        if debug:
                            print(f"MSE: {img_mse}, TOL: 10")
                        if img_mse > 10:
                            released = True
                            break
                    pokemon_at_0_pos = get_image()[124:132, 205:213] # update view
                    print(mse(pokemon_at_0_pos, bookend_check))
            add_to_stat_log(stats, "Box released")

    # go to first page and exit
    first_page(nx, controller_index)
    for i in range(10):
        nx.press_buttons(controller_index, [nxbt.Buttons.A], up=1.0)
    return

# starting position: off bike, on path, eggs in party, first col empty
def hatch(nx, controller_index, stats, debug=False):
    bike_check = np.array(Image.open("./check-imgs/bike-ref.png"))
    oh_check = np.array(Image.open("./check-imgs/oh-ref.png"))
    egg_ref = np.array(Image.open("./check-imgs/egg_at_0_0_ref.png"))
    bookend_ref = np.array(Image.open("./check-imgs/bookend.png"))

    pokemon_at_0_pos = get_image()[124:132, 205:213] # update view
    bookend_found = False


    # tolerances
    oh_tol = 24
    

    while not(bookend_found):
        
        # at this point, eggs in party, only col 0 is empty
        for empty_col in range(6):

            # Get on bike
            bike_toggle(nx, controller_index, debug)

            # Bike up and down until "Oh?" pops up
            ready_to_hatch = False
            while (ready_to_hatch == False):
                nx.press_buttons(controller_index, [nxbt.Buttons.DPAD_UP], down=11.0)
                nx.press_buttons(controller_index, [nxbt.Buttons.DPAD_DOWN], down=11.0)
                img = get_image()[398:425, 162:201]
                img_mse = mse(oh_check, img)
                if debug:
                        print(f"Looking for 'Oh?' MSE: {img_mse}, TOL: {oh_tol}")
                if img_mse < oh_tol:
                    ready_to_hatch = True
                    break

            # mash A 110 times to hatch
            for i in range(110):
                nx.press_buttons(controller_index, [nxbt.Buttons.A], up=1.0)

            # Update hatch #
            stats['hatched'] += 5
            with open("stats.json", "w") as f:
                json.dump(stats, f)

            # Get off bike and open the box
            bike_toggle(nx, controller_index)
            open_box(nx, controller_index, multiselect=True)

            # Move party to open col (empty_col)
            shiny_val = move_col(nx, controller_index, -1, empty_col, check_for_shiny=True)
            if shiny_val:
                return True
            
            if(empty_col < 5): # ensuring we stay within this box

                # Grab from next avail column (empty_col + 1) and place in party
                move_col(nx, controller_index, empty_col + 1, -1)

            else:

                # press R until we either see an egg or the bookmark pokemon
                pokemon_at_0_pos = get_image()[124:132, 205:213]
                indicator_found = False
                while(indicator_found == False):
                    nx.press_buttons(controller_index, [nxbt.Buttons.R], up=2.0)
                    pokemon_at_0_pos = get_image()[124:132, 205:213]

                    # if we see an egg, pick up (0,0)-(0,4)
                    if (mse(pokemon_at_0_pos, egg_ref) < 20):

                        indicator_found = True

                        # place first col in party
                        move_col(nx, controller_index, 0, -1)
                    
                    # if we see a bookend, exit
                    if (mse(pokemon_at_0_pos, bookend_ref) < 20):
                        indicator_found = True
                        bookend_found = True
                        break

            # spam b to get back to game view
            for i in range(15):
                nx.press_buttons(controller_index, [nxbt.Buttons.B], up=1.0)

# initial position expected
    # party consists of 6 pokemon (flame body, 5x eggs)
    # "bookmark" pokemon are at position (0,0) in box[-1] and box[max+1], and the view is somewhere in between
    # due to limitations of nxbt and unexpected dropped inputs, the number of boxes must be specified, despite the above condition (20 boxes are used in this example)
    # there are no eggs present in the boxes
    # the player is somewhere within solaceon town
    # box[-1] which consists of a bookmark at (0,0) must also have "dummy" pokemon at positions (5, 0) through (5, 4) to ensure that while we get eggs, no pokemon hatch
def masuda(num_boxes, debug=False):
    stats = None
    if os.path.isfile("stats.json"):
        with open("stats.json", "r") as f:
            stats = json.load(f)
    else:
        stats = {
            "eggs": 0,
            "issues": 0,
            "log": []
        }

    # Initialize an emulated controller and connect
    # to an available Switch.
    nx = nxbt.Nxbt()
    controller_index = nx.create_controller(
        nxbt.PRO_CONTROLLER,
        reconnect_address=nx.get_switch_addresses())
    nx.wait_for_connection(controller_index)

    add_to_stat_log(stats, "Controller Connected")

    time.sleep(5)

    POKEMON_PER_BOX = 30
    shiny_found = False

    while(shiny_found == False):
       #solaceon(nx, controller_index)
       #print("Heading to nursery man") # sometimes due to clouds, or the time of day, this can be buggy
       #return_val = False
       #while(return_val == False):
       #    return_val = move_to_nursery_man(nx, controller_index, debug)
       #send_message("Getting new eggs")
       #get_new_eggs(POKEMON_PER_BOX * num_boxes, nx, controller_index, stats, debug=True)
       send_message("Heading to bike path")
       return_val = False
       while not(return_val):
           return_val = move_to_bike_path(nx, controller_index, debug)
       send_message("Hatching")
       shiny_found = hatch(nx, controller_index, stats, debug=True)
       if shiny_found == True:
           send_message("Shiny found")
           return
       if shiny_found == False:
           print("No shinies found, releasing boxes")
       release_boxes(stats, nx, controller_index, debug=True)
       return

# Expected commandline input -- sudo python3 masuda.py [num_boxes]
if __name__ == "__main__":
#    print(get_picked_up_coords(debug=True))
    masuda(int(sys.argv[1]), debug=True) # repeatedly fetch eggs and hatch within the constraints of  boxes
#    init_bookends()
#    init_breed_species()
    send_message("No shiny :(")


