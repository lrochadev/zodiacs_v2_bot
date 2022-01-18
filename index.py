import pyautogui
import cv2
from random import random
import time
import sys
import os
import mss
import np
from pynput.mouse import Listener
import logging

totalCarsAcc = 3
forcePos = 1  # default
scrollForce = 93  # scroll windows force 3
executeSystem = True
threshold = 0.7
timeWaitClaim = 5
mouseInitX = 1752
mouseInitY = 472
mouseUnselectedYPlus = 48
mouseInitYPlus = 78
mouseBtnStartX = 1751
mouseBtnStartY = 494
lastRaceStatus = 1

driverAux = None
cont = 0
totalForce = 0
carsCount = 0
cars = 0

positionLast3 = [250, 150, 100]


def add_randomness(n, randomn_factor_size=None):
    if randomn_factor_size is None:
        randomness_percentage = 0.1
        randomn_factor_size = randomness_percentage * n

    random_factor = 2 * random() * randomn_factor_size
    if random_factor > 5:
        random_factor = 5
    without_average_random_factor = n - randomn_factor_size
    randomized_n = int(without_average_random_factor + random_factor)
    return int(randomized_n)


def move_to_with_randomness(x, y, t):
    pyautogui.moveTo(add_randomness(x, 10), add_randomness(y, 10), t + random() / 2)


def get_mouse_position():
    position = pyautogui.position()
    print(position)
    time.sleep(2)


def run_system():
    global cont, cars, carsCount, totalForce, mouseInitYPlus, scrollForce, lastRaceStatus, forcePos

    carsCount += 1

    if carsCount > totalCarsAcc:
        print("\n -------------------------------- End cars !!!")
        sys.exit(0)

    if carsCount > 1:
        totalForce += scrollForce

    global mouseBtnStartX, mouseBtnStartY
    global executeSystem, timeWaitClaim

    if executeSystem:
        error = False

        while True:
            if not error:
                # positions 8,9,10 ex: 10cars
                if carsCount > totalCarsAcc - 3:
                    rectangles = img_find_screen('Img/car-list.png', True, 0, mouseInitYPlus)
                    pyautogui.click()
                    pyautogui.scroll(-2000)
                    time.sleep(1)
                    pyautogui.scroll(-2000)

                    x, y, w, h = rectangles[len(rectangles) - 1]
                    position_y = positionLast3[totalCarsAcc - carsCount]

                    rectangles = img_find_screen('Img/car-list.png', True, 0, position_y)
                    move_to_with_randomness(x, y + position_y, 1)
                else:
                    img_find_screen('Img/car-list.png', True, 0, mouseInitYPlus)
                    pyautogui.click()
                    if carsCount > 1:
                        if lastRaceStatus == 1:
                            pyautogui.scroll(-scrollForce)
                        elif lastRaceStatus == 2:
                            pyautogui.scroll(-totalForce)

                time.sleep(1)
                pyautogui.click()

            rectangles = img_find_screen('Img/start-btn.png', True, 0, 10)
            pyautogui.click()

            if len(rectangles) > 0:

                rectangles = img_find_screen_time('Img/race-completed.png', False, 0, 0, 5)

                if len(rectangles) > 0:
                    print(str(carsCount) + " - Race Completed")
                    pyautogui.press('esc')
                    lastRaceStatus = 1
                    break
                else:
                    while True:
                        time.sleep(timeWaitClaim)
                        error = False
                        rectangles = img_find_screen('Img/check-result-btn.png', True, 0, 10)
                        if rectangles == "HtmlRequestError":
                            pyautogui.press('esc')
                            print("ERROR: HtmlRequestError")
                            error = True
                            break

                        if len(rectangles) > 0:
                            pyautogui.click()
                            while True:
                                rectangles = img_find_screen('Img/claim-btn.png', False, 0, 0)
                                if len(rectangles) > 0:
                                    pyautogui.press('esc')
                                    img_find_screen('Img/car-list.png', True, 0, 80)
                                    pyautogui.click()
                                    lastRaceStatus = 2
                                    break
                            break
    else:
        print(str(carsCount) + " - " + str(totalForce))


def print_screen():
    with mss.mss() as sct:
        monitor = sct.monitors[0]
        sct_img = np.array(sct.grab(monitor))
        return sct_img[:, :, :3]


def img_find_position(img_target):
    img = print_screen()
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    result = cv2.matchTemplate(img, img_target, cv2.TM_CCOEFF_NORMED)

    w = img_target.shape[1]
    h = img_target.shape[0]

    yloc, xloc = np.where(result >= threshold)

    rectangles = []
    for (x, y) in zip(xloc, yloc):
        rectangles.append([int(x), int(y), int(w), int(h)])
        rectangles.append([int(x), int(y), int(w), int(h)])

    rectangles, weights = cv2.groupRectangles(rectangles, 1, 0.2)
    return rectangles


def img_find_screen(imgPath, moveMouse, plusX, plusY):
    return img_find_screen_time(imgPath, moveMouse, plusX, plusY, 0)


def img_find_screen_time(imgPath, moveMouse, plusX, plusY, time_limit):
    rectangles = []

    time_limit = time_limit * 1000

    start_time = round(time.time() * 1000)

    img_target = cv2.imread(imgPath)
    img_target = cv2.cvtColor(img_target, cv2.COLOR_BGR2GRAY)

    verify_result = False
    img_target2 = None
    if 'check-result-btn' in imgPath:
        verify_result = True
        img_target2 = cv2.imread("Img/http-request-failed.png")
        img_target2 = cv2.cvtColor(img_target2, cv2.COLOR_BGR2GRAY)

    while True:

        if time_limit > 0:
            current_time = round(time.time() * 1000)
            tm = current_time - start_time
            if tm >= time_limit:
                return []

        if verify_result:
            rectangles2 = img_find_position(img_target2)
            if len(rectangles2) > 0:
                return "HtmlRequestError"

        rectangles = img_find_position(img_target)
        if len(rectangles) > 0:
            x, y, w, h = rectangles[len(rectangles) - 1]
            x += plusX
            y += plusY
            if moveMouse:
                move_to_with_randomness(x, y, 1)
            return rectangles

        time.sleep(0.1)

    return rectangles


def main():
    global totalForce, forcePos, carsCount, lastRaceStatus, positionLast3

    if forcePos > 1:
        carsCount = forcePos - 1
        totalForce = scrollForce * (forcePos - 2)
        lastRaceStatus = 2
    while True:
        run_system()
        time.sleep(0.1)


try:
    main()
except KeyboardInterrupt:
    print("\n -------------------------------- Bye !!!")
    sys.exit(0)
