# Author: Kyle Mathias

import os
import cv2
import numpy as np
import pyautogui 
import time
import psutil  
import mss
import sys

# Function to get the correct resource path whether the app is frozen (as an .exe) or running from the source
def get_resource_path(relative_path):
    """ Get the absolute path to a resource, works whether the app is frozen or not. """
    if getattr(sys, 'frozen', False):  # If running from PyInstaller bundle
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

LOG = True
DIFFICULTY = "INSANE"
APP_NAME = "Super Mechs.exe"

# Define base path for resources using the new helper function
RESOURCES_DIR = get_resource_path('resources')
BUTTONS_DIR = os.path.join(RESOURCES_DIR, 'buttons')
SCREENS_DIR = os.path.join(RESOURCES_DIR, 'screens')

# Define image paths using the helper function

ABORT_IMAGE_PATH = os.path.join(BUTTONS_DIR, "ABORT.png")
AUTO_IMAGE_PATH = os.path.join(BUTTONS_DIR, "AUTO.png")
BACK_IMAGE_PATH = os.path.join(BUTTONS_DIR, "BACK.png")
BATTLE_IMAGE_PATH = os.path.join(BUTTONS_DIR, "BATTLE.png")
CAMPAIGN_IMAGE_PATH = os.path.join(BUTTONS_DIR, "CAMPAIGN.png")
CLOSE_IMAGE_PATH = os.path.join(BUTTONS_DIR, "CLOSE.png")
HARD_IMAGE_PATH = os.path.join(BUTTONS_DIR, "HARD.png")
INSANE_IMAGE_PATH = os.path.join(BUTTONS_DIR, "INSANE.png")
OD8_IMAGE_PATH = os.path.join(BUTTONS_DIR, "OD8.png")
OK_IMAGE_PATH = os.path.join(BUTTONS_DIR, "OK.png")
OK2_IMAGE_PATH = os.path.join(BUTTONS_DIR, "OK2.png")
SELECT_IMAGE_PATH = os.path.join(BUTTONS_DIR, "SELECT.png")
SMAC_MONEY_IMAGE_PATH = os.path.join(BUTTONS_DIR, "SMAC-MONEY.png")
SPEED_IMAGE_PATH = os.path.join(BUTTONS_DIR, "SPEED.png")
TEAMS_IMAGE_PATH = os.path.join(BUTTONS_DIR, "TEAMS.png")
WORKSHOP_IMAGE_PATH = os.path.join(BUTTONS_DIR, "WORKSHOP.png")
X_IMAGE_PATH = os.path.join(BUTTONS_DIR, "X.png")
CONTINUE_IMAGE_PATH = os.path.join(BUTTONS_DIR, "CONTINUE.png")

MAIN_SCREEN_IMAGE_PATH = os.path.join(SCREENS_DIR, "MainScreen.png")
RESTORATION_OF_EARTH_IMAGE_PATH = os.path.join(SCREENS_DIR, "RestorationOfEarth.png")
VICTORY_IMAGE_PATH = os.path.join(SCREENS_DIR, "Victory.png")
CLAIM_REWARDS_IMAGE_PATH = os.path.join(SCREENS_DIR, "ClaimRewards.png")
NOT_ENOUGH_FUEL_IMAGE_PATH = os.path.join(SCREENS_DIR, "NotEnoughFuel.png")


# Other variables
USER_DIR = os.path.expanduser("~")  # Get the user's home directory
APP_PATH = os.path.join(USER_DIR, "AppData", "Local", "SuperMechs", APP_NAME)


# Function to find the center of an image on the screen
def find_image(image_path, threshold = 0.8):
    if not os.path.isfile(image_path):
        print(f"Image file not found: {image_path}") if LOG else None
        return None

    print("Capturing screen...") if LOG else None

    with mss.mss() as sct:
        screen_img = sct.grab(sct.monitors[1])  # Grab the first monitor

    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)  # Read the image
    screen_img = np.array(screen_img)

    # Get template dimensions
    h, w = image.shape[:2]

    # Apply template Matching
    res = cv2.matchTemplate(screen_img, image, cv2.TM_CCOEFF_NORMED)  # Match the template
    print("Template matching completed.") if LOG else None

    # Get min and max values of the result
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    # Set a threshold for matching

    if max_val >= threshold:  # Check if the maximum value exceeds the threshold
        center_x = max_loc[0] + w // 2
        center_y = max_loc[1] + h // 2
        print(f"Image found at coordinates: ({center_x}, {center_y})") if LOG else None
        return center_x, center_y

    print(f"Image not found: {image_path}") if LOG else None
    return None


def is_app_running(app_name):
    """Check if a process with the given name is running."""
    for process in psutil.process_iter(['name']):
        if app_name.lower() in process.info['name'].lower():
            return process
    return None


def kill_app(app_name):
    killed_processes = []
    
    for process in psutil.process_iter(attrs=['pid', 'name']):
        try:
            if process.info['name'] == app_name:
                process.terminate()  # Attempt to terminate gracefully
                process.wait(timeout=5)  # Wait for it to close
                killed_processes.append(process.info['pid'])
        except psutil.NoSuchProcess:
            # Process has already terminated
            continue
        except psutil.AccessDenied:
            print(f"Access denied when trying to terminate {app_name} (PID: {process.info['pid']})")
        except Exception as e:
            # Handle any other exceptions
            print(f"Failed to terminate {app_name}: {e}")

    if killed_processes:
        print(f"Terminated {len(killed_processes)} instance(s) of {app_name}: {killed_processes}") if LOG else None
    else:
        print(f"No instances of {app_name} found.") if LOG else None


def main():
    initial_run = True
    # Main loop adjustments for handling watch sequence
    while True:
        print("Checking if application is already running...") if LOG else None
        if is_app_running(APP_NAME):
            print("Application is already running. Terminating it...") if LOG else None
            kill_app(APP_NAME)
            time.sleep(5)  # Wait for 5 seconds to ensure it's terminated

        print("Opening the application...") if LOG else None
        os.startfile(APP_PATH)  # Open the application
        time.sleep(13)  # Wait for the application to load

        # Loop to check for images
        while True:
            # Check for the CLOSE button
            close_coords = find_image(CLOSE_IMAGE_PATH)
            if close_coords:
                print("CLOSE button detected.") if LOG else None
                pyautogui.click(*close_coords)  # Using pyautogui to click
                time.sleep(2)

            x_coords = find_image(X_IMAGE_PATH)
            if x_coords:
                print("X button detected.") if LOG else None
                pyautogui.click(*x_coords)  # Using pyautogui to click
                time.sleep(2)

            # Check for the main screen
            main_screen_coords = find_image(MAIN_SCREEN_IMAGE_PATH)
            if main_screen_coords:
                print("Main screen detected.") if LOG else None
                time.sleep(2)  # Wait for the screen to stabilize

                # Set grind team
                while initial_run:
                    initial_run = False

                    workshop_coords = find_image(WORKSHOP_IMAGE_PATH)
                    if workshop_coords:
                        print(f"Clicking on WORKSHOP button at {workshop_coords}.") if LOG else None
                        pyautogui.click(*workshop_coords)
                        time.sleep(2)

                        x2_coords = find_image(X_IMAGE_PATH)
                        if x2_coords:
                            print(f"Clicking on WORKSHOP button at {x2_coords}.") if LOG else None
                            pyautogui.click(*x2_coords)
                            time.sleep(2)

                        teams_coords = find_image(TEAMS_IMAGE_PATH)
                        if teams_coords:
                            print(f"Clicking on TEAMS button at {teams_coords}.") if LOG else None
                            pyautogui.click(*teams_coords)
                            time.sleep(1)

                            team_coords = find_image(SMAC_MONEY_IMAGE_PATH)
                            if team_coords:
                                print(f"Clicking on SMAC-MONEY button at {team_coords}.") if LOG else None
                                pyautogui.click(*team_coords)
                                time.sleep(1)

                                select_coords = find_image(SELECT_IMAGE_PATH)
                                if select_coords:
                                    print(f"Clicking on SELECT button at {select_coords}.") if LOG else None
                                    pyautogui.click(*select_coords)
                                    time.sleep(2)

                                    back_coords = find_image(BACK_IMAGE_PATH)
                                    if back_coords:
                                        print(f"Clicking on BACK button at {back_coords}.") if LOG else None
                                        pyautogui.click(*back_coords)
                                        time.sleep(2)
                                        break


                                    else:
                                        print("Closing application due to BACK ERROR.")
                                        kill_app(APP_NAME)
                                        exit(-1)
                                else:
                                    print("Closing application due to SELECT ERROR.")
                                    kill_app(APP_NAME)
                                    exit(-1)
                            else:
                                print("Closing application. Team SMAC-MONEY does not exist.")
                                kill_app(APP_NAME)
                                exit(-1)
                        else:
                            print("Closing application due to TEAMS ERROR.")
                            kill_app(APP_NAME)
                            exit(-1)
                    else:
                        print("Closing application due to WORKSHOP ERROR.")
                        kill_app(APP_NAME)
                        exit(-1)

                # Check for CAMPAIGN
                campaign_coords = find_image(CAMPAIGN_IMAGE_PATH)
                if campaign_coords:
                    print("CAMPAIGN button detected.") if LOG else None
                    pyautogui.click(*campaign_coords)
                    time.sleep(2)

                    restoration_coords = find_image(RESTORATION_OF_EARTH_IMAGE_PATH)
                    if restoration_coords:
                        print("Restoration of Earth detected.") if LOG else None
                        pyautogui.click(*restoration_coords)
                        time.sleep(2)

                        while True:
                            od8_coords = find_image(OD8_IMAGE_PATH)
                            if od8_coords:
                                print("OD8 detected.") if LOG else None
                                pyautogui.click(*od8_coords)
                                time.sleep(1)

                                if DIFFICULTY == "HARD":
                                    hard_coords = find_image(HARD_IMAGE_PATH, 1)
                                    if hard_coords:
                                        print("HARD detected.") if LOG else None
                                        pyautogui.click(*hard_coords)
                                        time.sleep(0.5)
                                elif DIFFICULTY == "INSANE":
                                    insane_coords = find_image(INSANE_IMAGE_PATH, 0.95)
                                    if insane_coords:
                                        print("INSANE detected.") if LOG else None
                                        pyautogui.click(*insane_coords)
                                        time.sleep(0.5)

                                battle_coords = find_image(BATTLE_IMAGE_PATH)
                                if battle_coords:
                                    print("BATTLE detected.") if LOG else None
                                    pyautogui.click(*battle_coords)
                                    time.sleep(2)

                                    not_enough_fuel_coords = find_image(NOT_ENOUGH_FUEL_IMAGE_PATH)
                                    if not_enough_fuel_coords:
                                        print("Not Enough Fuel, come back when fuel is enough.")
                                        kill_app(APP_NAME)
                                        exit(0)
                                    
                                    speed_coords = find_image(SPEED_IMAGE_PATH)
                                    if speed_coords:
                                        print("X1 SPEED detected.") if LOG else None
                                        pyautogui.click(*speed_coords)
                                        time.sleep(0.5)

                                    auto_coords = find_image(AUTO_IMAGE_PATH, 0.95)
                                    if auto_coords:
                                        print("AUTO OFF detected.") if LOG else None
                                        pyautogui.click(*auto_coords)
                                        time.sleep(0.5)

                                    victory_coords = find_image(VICTORY_IMAGE_PATH)
                                    abort_coords = find_image(ABORT_IMAGE_PATH)
                                    while not victory_coords and not abort_coords:
                                        time.sleep(5)
                                        victory_coords = find_image(VICTORY_IMAGE_PATH)
                                        abort_coords = find_image(ABORT_IMAGE_PATH)
                                    if victory_coords:
                                        print("VICTORY detected.") if LOG else None
                                        pyautogui.click(*victory_coords)
                                        time.sleep(3)

                                        continue_coords = find_image(CONTINUE_IMAGE_PATH)
                                        if continue_coords:
                                            print("CONTINUE detected.") if LOG else None
                                            pyautogui.click(*continue_coords)
                                            time.sleep(2)

                                        claim_rewards_coords = find_image(CLAIM_REWARDS_IMAGE_PATH)
                                        if claim_rewards_coords:
                                            print("CLAIM REWARDS detected.") if LOG else None
                                            pyautogui.click(*claim_rewards_coords)
                                            time.sleep(5)
                                            pyautogui.click(*claim_rewards_coords)
                                            time.sleep(0.5)
                                            pyautogui.click(*claim_rewards_coords)
                                            time.sleep(2)

                                            ok2_coords = find_image(OK2_IMAGE_PATH)
                                            if ok2_coords:
                                                print("OK detected.") if LOG else None
                                                pyautogui.click(*ok2_coords)
                                                time.sleep(2)

                                    elif abort_coords:
                                        print("ABORT detected.") if LOG else None
                                        pyautogui.click(*abort_coords)
                                        time.sleep(3)

                                        continue_coords = find_image(CONTINUE_IMAGE_PATH)
                                        if continue_coords:
                                            print("CONTINUE detected.") if LOG else None
                                            pyautogui.click(*continue_coords)
                                            time.sleep(2)

                                        x_coords = find_image(X_IMAGE_PATH)
                                        if x_coords:
                                            print("X detected.") if LOG else None
                                            pyautogui.click(*x_coords)
                                            time.sleep(2)

                                    x3_coords = find_image(X_IMAGE_PATH)
                                    if x3_coords:
                                        print(f"Clicking on WORKSHOP button at {x3_coords}.") if LOG else None
                                        pyautogui.click(*x3_coords)
                                        time.sleep(2)

                                else:
                                    print("BATTLE not found. Killing Instance")
                                    kill_app(APP_NAME)
                                    exit(-1)
                            else:
                                print("OD8 not found. Killing Instance")
                                kill_app(APP_NAME)
                                exit(-1)
                    else:
                        print("Restoration of Earth not found. Killing Instance")
                        kill_app(APP_NAME)
                        exit(-1)       
                else:
                    print("CAMPAIGN button not found. Killing Instance")
                    kill_app(APP_NAME)
                    exit(-1)
            else:
                print("Main screen not found. Waiting for 5 seconds...") if LOG else None
                time.sleep(5)  # Wait before trying again


main()

