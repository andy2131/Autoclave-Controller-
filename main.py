import random
import time
import sys
sys.path.append('../')

from Common_Libraries.p2_lib import *

import os
from Common_Libraries.repeating_timer_lib import repeating_timer

def update_sim ():
    try:
        arm.ping()
    except Exception as error_update_sim:
        print (error_update_sim)

arm = qarm()

update_thread = repeating_timer(2, update_sim)

def identify(_id):
    """

    A function to return the drop-off coordinates of 6 containers based on their ID.
    Stores all drop-off coordinates into a list corresponding to the order of the container’s id
    and only return the appopriate one
    
    """
    #Store all drop-off coordinates into corresponding variables
    small_red = [-0.5873, 0.2373, 0.364]
    small_blue = [0.0, 0.6334, 0.364]
    small_green = [0.0, -0.6334, 0.364]
    big_red = [-0.3459, 0.150, 0.3]
    big_blue = [0, 0.385, 0.3]
    big_green = [0, -0.385, 0.3]
    #Create a list with all drop-off coordinates with appropriate index relative to their ID 
    coordinates = [small_red, small_green, small_blue, big_red, big_green, big_blue]
    #Return the drop-off coordinate based on the id  
    return coordinates[_id-1]

def move_end_effector(_id, left, right):
    """

    This function will move the q-arm to the drop-off, pick-up, and home position
    based on the condition of the left and right reading of the emg sensor. 

    """
    #Store the drop-off coordinate of the container 
    drop_coordinates = identify(_id)
    if right == 0:
        #If right arm equal to 0 and left arm greater than 0.7 move arm to drop-off position
        if left > 0.7:
            arm.move_arm(drop_coordinates[0],drop_coordinates[1],drop_coordinates[2])
            time.sleep(2)
        #Else if left arm greater than 0.5 move arm to home position
        elif left > 0.5:
            arm.move_arm(0.4064, 0.0, 0.4823)
            time.sleep(2)
        #Else if left arm greater than 0.3 move arm to pick-up position
        elif left > 0.3:
            arm.move_arm(0.4756, 0.0, 0.0036)
            time.sleep(2)

def control_gripper(left, right):
    """ 

    A function to open and close the gripper 

    """
    #Create a variable gripper_position to keep track if gripper is open or closed. 
    gripper_position = 0            
    if left == 0:
        #If left arm equal to 0 and right arm greater than 0.5 set gripper_position to -40 (open gripper)
        if right > 0.5: 
            gripper_position = -40
            arm.control_gripper(gripper_position)
            time.sleep(2)
        #Else if left arm equal to 0 and right arm greater than 0.3 set gripper_position to 40 (close gripper)
        elif right > 0.3:
            gripper_position = 40
            arm.control_gripper(gripper_position)
            time.sleep(2)
    return gripper_position

def open_drawer(_id, left, right):
    """ 

    A function to open and close the autoclave drawer 

    """
    #Create a variable is_open to keep track if autoclave drawer is open or closed.
    is_open = True 
    if left > 0.5 and right > 0.5:
        #If left and right arm both greater than 0.5, set is_open to False (close drawer) 
        is_open = False
        #Close different colored drawers depending on the id.
        if _id == 4:
            arm.open_red_autoclave(is_open)
            time.sleep(2)
        elif _id == 5:
            arm.open_green_autoclave(is_open)
            time.sleep(2)
        elif _id == 6:
            arm.open_blue_autoclave(is_open)
            time.sleep(2)
    elif left > 0.3 and right > 0.3:
        #Else if left and right arm both greater than 0.3, set is_open to True (open drawer)
        is_open = True
        #Open different colored drawers depending on the id.
        if _id == 4:
            arm.open_red_autoclave(is_open)
            time.sleep(2)
        elif _id == 5:
            arm.open_green_autoclave(is_open)
            time.sleep(2)
        elif _id == 6:
            arm.open_blue_autoclave(is_open)
            time.sleep(2)
    return is_open

def main():
    """ 

    Main function combines all the above functions in a logical way in order to control the robot arm
    based on the real time emg sensor reading. 

    """
    #Create a list of 6 booleans to store if any of the container is picked. 
    picked = [False, False, False, False, False, False]

    #While there is still a container not picked, run while loop to control the robot arm and pick up
    while False in picked:
        #Reset the robot arm to home
        arm.home()
        #Generate random id from 1-6
        _id = random.randint(1,6)
        #If the generated id is already picked, generate one that's not
        while picked[_id-1] == True:
            _id = random.randint(1,6)
        #Spawn corresponding container depending on the id        
        arm.spawn_cage(_id)
        
        while True:
            #Constantly read the left and right arm value
            left = arm.emg_left()
            right = arm.emg_right()
            #Call all the functions to control the robot arm in real time
            move_end_effector(_id ,left, right)
            open_drawer(_id, left, right)
            gripper_position=control_gripper(left, right)
            #Create a variable position to keep track of the real time arm position
            position = [arm.effector_position()[0],arm.effector_position()[1],arm.effector_position()[2]]
            #If arm position is at drop off location and gripper is opened (container is dropped off) 
            if position == identify(_id) and gripper_position == -40:
                #If the container id is 4,5,6 (big), check if the autoclave drawer is closed 
                while _id in [4,5,6]:
                    left = arm.emg_left()
                    right = arm.emg_right()
                    is_open = open_drawer(_id, left, right)
                    #When autoclave drawer is closed, break the while loop
                    if is_open == False:
                        break 
                #After all conditions are met, set the boolean in picked corresponding to the id to True
                picked[_id-1] = True
                time.sleep(2)
                #Break the while loop and return to the beginning to check if there are any containers still not picked
                break
    #After all containers are placed, reset the arm to home and print "All containers are placed"    
    arm.home()
    print("All containers are placed")

main()
        

