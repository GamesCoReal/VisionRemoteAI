import pyautogui
import time
import math
import random

from rich.console import Console
from rich_pixels import Pixels


console = Console()


def Format_time(seconds):
    milliseconds = round((seconds % 1) * 1000)
    total_seconds = int(seconds)

    if milliseconds == 1000:
        milliseconds = 0
        total_seconds += 1

    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    remaining_seconds = total_seconds % 60

    parts = []

    if hours:
        parts.append(
            f"{hours} hour" + ("s" if hours != 1 else "")
        )

    if minutes:
        parts.append(
            f"{minutes} minute" + ("s" if minutes != 1 else "")
        )

    if remaining_seconds:
        parts.append(
            f"{remaining_seconds} second"
            + ("s" if remaining_seconds != 1 else "")
        )

    if milliseconds:
        parts.append(
            f"{milliseconds} millisecond"
            + ("s" if milliseconds != 1 else "")
        )

    if not parts:
        return "0 seconds"

    return " ".join(parts)


def View_screen():
    screenshot = pyautogui.screenshot()

    console.print(
        Pixels.from_image(
            screenshot,
            resize_to=(100, 40)
        )
    )


def Human_move(x, y):
    start_x, start_y = pyautogui.position()

    screen_width, screen_height = pyautogui.size()

    distance = math.hypot(
        x - start_x,
        y - start_y
    )

    screen_diagonal = math.hypot(
        screen_width,
        screen_height
    )

    speed = random.uniform(1.5, 2.3)

    distance_ratio = distance / screen_diagonal

    duration = distance_ratio / speed

    steps = max(int(duration * 120), 1)

    for i in range(1, steps + 1):
        progress = i / steps

        smooth = progress * progress * (3 - 2 * progress)

        current_x = start_x + (x - start_x) * smooth
        current_y = start_y + (y - start_y) * smooth

        pyautogui.moveTo(
            current_x,
            current_y,
            duration=0
        )

        if duration > 0:
            time.sleep(duration / steps)

    return (
        f"completed: mouse move, "
        f"start: ({start_x}, {start_y}), "
        f"end: ({x}, {y}), "
        f"for {Format_time(duration)}"
    )


def Click(button, x, y, duration):
    Human_move(x, y)

    if button == "left":
        pyautogui.mouseDown(button="left")

    elif button == "right":
        pyautogui.mouseDown(button="right")

    else:
        raise ValueError(
            "button must be 'left' or 'right'"
        )

    time.sleep(duration)

    pyautogui.mouseUp(button=button)

    return (
        f"completed: {button} click, "
        f"start: ({x}, {y}), "
        f"for {Format_time(duration)}"
    )


def Scroll(direction, startX, startY, duration, speed):
    Human_move(startX, startY)

    if direction not in ("up", "down"):
        raise ValueError(
            "direction must be 'up' or 'down'"
        )

    start_time = time.time()

    while time.time() - start_time < duration:

        if direction == "up":
            pyautogui.scroll(speed)
        else:
            pyautogui.scroll(-speed)

        time.sleep(0.05)

    return (
        f"completed: scroll {direction}, "
        f"start: ({startX}, {startY}), "
        f"for {Format_time(duration)}, "
        f"speed: {speed}"
    )


def Swipe(startX, startY, endX, endY):
    swipe_duration = 0.5

    Human_move(startX, startY)

    pyautogui.dragTo(
        endX,
        endY,
        duration=swipe_duration
    )

    return (
        f"completed: swipe, "
        f"start: ({startX}, {startY}), "
        f"end: ({endX}, {endY}), "
        f"for {Format_time(swipe_duration)}"
    )


def Type(string):
    pyautogui.write(string)

    return (
        f"completed: type, "
        f"text: {string!r}"
    )


def Wait(duration):
    time.sleep(duration)

    return (
        f"completed: wait, "
        f"for {Format_time(duration)}"
    )


def Done(completed=True):
    return f"completed: {completed}"
