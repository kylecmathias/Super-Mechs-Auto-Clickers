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

APP_NAME = "Super Mechs.exe"

# Define base path for resources using the new helper function
RESOURCES_DIR = get_resource_path('resources')
BUTTONS_DIR = os.path.join(RESOURCES_DIR, 'buttons')
SCREENS_DIR = os.path.join(RESOURCES_DIR, 'screens')

# Define image paths using the helper function
CLOSE_IMAGE_PATH = os.path.join(BUTTONS_DIR, "CLOSE.png")
RIGHT_IMAGE_PATH = os.path.join(BUTTONS_DIR, "RIGHT.png")
RIGHT_PRESSED_IMAGE_PATH = os.path.join(BUTTONS_DIR, "RIGHT PRESSED.png")
X_IMAGE_PATH = os.path.join(BUTTONS_DIR, "X.png")
STORE_IMAGE_PATH = os.path.join(BUTTONS_DIR, "STORE.png")
MAIN_SCREEN_IMAGE_PATH = os.path.join(SCREENS_DIR, "MainScreen.png")
WATCH_NOW_IMAGE_PATH = os.path.join(BUTTONS_DIR, "WATCH NOW.png")
WATCH_ERROR_IMAGE_PATH = os.path.join(SCREENS_DIR, "WatchError.png")
CLAIM_REWARD_IMAGE_PATH = os.path.join(BUTTONS_DIR, "CLAIM REWARD.png")
OK_IMAGE_PATH = os.path.join(BUTTONS_DIR, "OK.png")

# Other variables
USER_DIR = os.path.expanduser("~")  # Get the user's home directory
APP_PATH = os.path.join(USER_DIR, "AppData", "Local", "SuperMechs", APP_NAME)


# Function to find the center of an image on the screen
def find_image(image_path):
    if not os.path.isfile(image_path):
        print(f"Image file not found: {image_path}")
        return None

    print("Capturing screen...")

    with mss.mss() as sct:
        screen_img = sct.grab(sct.monitors[1])  # Grab the first monitor

    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)  # Read the image
    screen_img = np.array(screen_img)

    # Get template dimensions
    h, w = image.shape[:2]

    # Apply template Matching
    res = cv2.matchTemplate(screen_img, image, cv2.TM_CCOEFF_NORMED)  # Match the template
    print("Template matching completed.")

    # Get min and max values of the result
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    # Set a threshold for matching
    threshold = 0.8  # Adjust this value as needed

    if max_val >= threshold:  # Check if the maximum value exceeds the threshold
        center_x = max_loc[0] + w // 2
        center_y = max_loc[1] + h // 2
        print(f"Image found at coordinates: ({center_x}, {center_y})")
        return center_x, center_y

    print(f"Image not found: {image_path}")
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
        print(f"Terminated {len(killed_processes)} instance(s) of {app_name}: {killed_processes}")
    else:
        print(f"No instances of {app_name} found.")


def handle_watch_now_sequence():
    """Handles the flow after clicking the WATCH NOW button."""
    # Check for the "CLAIM REWARD" button immediately after clicking "WATCH NOW"
    while True:
        claim_reward_coords = find_image(CLAIM_REWARD_IMAGE_PATH)
        if claim_reward_coords:
            print("CLAIM REWARD button detected. Waiting for 16 seconds before clicking...")
            time.sleep(16)  # Wait for 16 seconds
            pyautogui.click(*claim_reward_coords)  # Click the "CLAIM REWARD" button

            # Now enter a loop to check for the "OK" button
            
            time.sleep(2)
            ok_coords = find_image(OK_IMAGE_PATH)
            if ok_coords:
                print("OK button detected. Clicking OK.")
                pyautogui.click(*ok_coords)
                time.sleep(1)
                return True  # Successfully handled "CLAIM REWARD" and "OK"
            else:
                print("OK button not found. Retrying...")
                time.sleep(5)  # Wait before trying again

        # If "CLAIM REWARD" is not found, check for the "OK" button
        else:
            print("CLAIM REWARD not found. Checking for OK button instead...")
            ok_coords = find_image(OK_IMAGE_PATH)
            if ok_coords:
                print("OK button detected.")
                pyautogui.click(*ok_coords)  # Click "OK" button
                time.sleep(1)
                return False  # Return False to indicate an error and restart process
            else:
                print("Neither CLAIM REWARD nor OK button found. Continuing to next loop.")
                return False

def main():
    # Main loop adjustments for handling watch sequence
    while True:
        print("Checking if application is already running...")
        if is_app_running(APP_NAME):
            print("Application is already running. Terminating it...")
            kill_app(APP_NAME)
            time.sleep(5)  # Wait for 5 seconds to ensure it's terminated

        print("Opening the application...")
        os.startfile(APP_PATH)  # Open the application
        time.sleep(13)  # Wait for the application to load

        # Loop to check for images
        while True:
            # Check for the CLOSE button
            close_coords = find_image(CLOSE_IMAGE_PATH)
            if close_coords:
                print("CLOSE button detected.")
                pyautogui.click(*close_coords)  # Using pyautogui to click
                time.sleep(2)

            x_coords = find_image(X_IMAGE_PATH)
            if x_coords:
                print("X button detected.")
                pyautogui.click(*x_coords)  # Using pyautogui to click
                time.sleep(2)

            # Check for the main screen
            main_screen_coords = find_image(MAIN_SCREEN_IMAGE_PATH)
            if main_screen_coords:
                print("Main screen detected.")
                time.sleep(2)  # Wait for the screen to stabilize

                # Click on the specific button to open the store
                store_button_coords = find_image(STORE_IMAGE_PATH)
                if store_button_coords:
                    print(f"Clicking on store button at {store_button_coords}.")
                    pyautogui.click(*store_button_coords)
                    time.sleep(3)
                else:
                    print("Closing application due to STORE ERROR.")
                    kill_app(APP_NAME)
                    continue  # Restart the loop

                # Check for "watch now"
                watch_now_coords = find_image(WATCH_NOW_IMAGE_PATH)
                if watch_now_coords:
                    print("WATCH NOW button detected.")
                    pyautogui.click(*watch_now_coords)
                    time.sleep(1)

                    # Handle the sequence after clicking WATCH NOW
                    if not handle_watch_now_sequence():
                        print("Error occurred. Killing Instance.")
                        kill_app(APP_NAME)
                        break  # Restart the loop if error was detected

                    break  # Exit the loop once reward is claimed or OK is pressed
                else:
                    print("WATCH NOW button not found, checking for right arrow")
                    while True:
                        right_coords = find_image(RIGHT_IMAGE_PATH)
                        right_pressed_coords = find_image(RIGHT_PRESSED_IMAGE_PATH)
                        if right_coords or right_pressed_coords:
                            print("RIGHT button found, scrolling right")
                            pyautogui.click(*right_coords) if right_coords else pyautogui.click(*right_pressed_coords)
                            time.sleep(2)
                        else:
                            print("RIGHT button not found, checking for WATCH NOW")
                            time.sleep(1)
                            watch_now_coords = find_image(WATCH_NOW_IMAGE_PATH)
                            if watch_now_coords:
                                print("WATCH NOW button detected.")
                                pyautogui.click(*watch_now_coords)
                                time.sleep(1)

                                if not handle_watch_now_sequence():
                                    print("Error occurred. Killing Instance.")
                                    kill_app(APP_NAME)

                                break  # Exit the loop once reward is claimed or OK is pressed
                            else:
                                print("WATCH NOW button not found, exiting...")
                                kill_app(APP_NAME)
                                exit()
                    break
            else:
                print("Main screen not found. Waiting for 5 seconds...")
                time.sleep(5)  # Wait before trying again


main()
