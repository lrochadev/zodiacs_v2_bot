import pyautogui
import cv2
from random import random
import time
import sys
import mss
import np

total_cars_acc = 3
force_pos = 1
# scroll windows force 3
scroll_force = 93
execute_system = True
threshold = 0.7
time_wait_claim = 5
mouse_init_x = 1752
mouse_init_y = 472
mouse_unselected_y_plus = 48
mouse_init_y_plus = 78
mouse_btn_start_x = 1751
mouse_btn_start_y = 494
last_race_status = 1
driver_aux = None
total_force = 0
cars_count = 0
cars = 0
position_last_3 = [250, 150, 100]


def add_randomness(n, random_factor_size=None):
    if random_factor_size is None:
        randomness_percentage = 0.1
        random_factor_size = randomness_percentage * n

    random_factor = 2 * random() * random_factor_size

    if random_factor > 5:
        random_factor = 5

    without_average_random_factor = n - random_factor_size
    randomized_n = int(without_average_random_factor + random_factor)

    return int(randomized_n)


def move_to_with_randomness(x, y, t):
    pyautogui.moveTo(add_randomness(x, 10), add_randomness(y, 10), t + random() / 2)


def run_system():
    global cars, cars_count, total_force, mouse_init_y_plus, scroll_force, last_race_status, force_pos
    cars_count += 1

    if cars_count > total_cars_acc:
        print("\n -------------------------------- End cars !!!")
        sys.exit(0)

    if cars_count > 1:
        total_force += scroll_force

    global mouse_btn_start_x, mouse_btn_start_y
    global execute_system, time_wait_claim

    if execute_system:
        error = False

        while True:
            if not error:
                if cars_count > total_cars_acc - 3:
                    rectangles = img_find_screen('Img/car-list.png', True, 0, mouse_init_y_plus)
                    pyautogui.click()
                    pyautogui.scroll(-2000)
                    time.sleep(1)
                    pyautogui.scroll(-2000)

                    x, y, w, h = rectangles[len(rectangles) - 1]
                    position_y = position_last_3[total_cars_acc - cars_count]

                    rectangles = img_find_screen('Img/car-list.png', True, 0, position_y)
                    move_to_with_randomness(x, y + position_y, 1)
                else:
                    img_find_screen('Img/car-list.png', True, 0, mouse_init_y_plus)
                    pyautogui.click()
                    if cars_count > 1:
                        if last_race_status == 1:
                            pyautogui.scroll(-scroll_force)
                        elif last_race_status == 2:
                            pyautogui.scroll(-total_force)

                time.sleep(1)
                pyautogui.click()

            rectangles = img_find_screen('Img/start-btn.png', True, 0, 10)
            pyautogui.click()

            if len(rectangles) > 0:

                rectangles = img_find_screen_time('Img/race-completed.png', False, 0, 0, 5)

                if len(rectangles) > 0:
                    print(str(cars_count) + " - Race Completed")
                    pyautogui.press('esc')
                    last_race_status = 1
                    break
                else:
                    while True:
                        time.sleep(time_wait_claim)
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
                                    last_race_status = 2
                                    break
                            break
    else:
        print(str(cars_count) + " - " + str(total_force))


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


def img_find_screen(img_path, move_mouse, plus_x, plus_y):
    return img_find_screen_time(img_path, move_mouse, plus_x, plus_y, 0)


def img_find_screen_time(img_path, move_mouse, plus_x, plus_y, time_limit):
    rectangles = []

    time_limit = time_limit * 1000

    start_time = round(time.time() * 1000)

    img_target = cv2.imread(img_path)
    img_target = cv2.cvtColor(img_target, cv2.COLOR_BGR2GRAY)

    verify_result = False
    img_target2 = None
    if 'check-result-btn' in img_path:
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
            x += plus_x
            y += plus_y
            if move_mouse:
                move_to_with_randomness(x, y, 1)
            return rectangles

        time.sleep(0.1)

    return rectangles


def main():
    global total_force, force_pos, cars_count, last_race_status, position_last_3

    if force_pos > 1:
        cars_count = force_pos - 1
        total_force = scroll_force * (force_pos - 2)
        last_race_status = 2
    while True:
        run_system()
        time.sleep(0.1)


try:
    main()
except KeyboardInterrupt:
    print("\n -------------------------------- Bye !!!")
    sys.exit(0)
