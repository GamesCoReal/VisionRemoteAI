import pyautogui
import time


def Format_time(seconds):
    milliseconds = round((seconds % 1) * 1000)
    total_seconds = int(seconds)

    # Handle rounding 999.5 milliseconds -> 1 second
    if milliseconds == 1000:
        milliseconds = 0
        total_seconds += 1

    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    remaining_seconds = total_seconds % 60

    parts = []

    if hours:
        parts.append(f"{hours} hour" + ("s" if hours != 1 else ""))

    if minutes:
        parts.append(f"{minutes} minute" + ("s" if minutes != 1 else ""))

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


def Click(button, x, y, duration):
    pyautogui.moveTo(x, y)

    if button == "left":
        pyautogui.mouseDown(button="left")
    elif button == "right":
        pyautogui.mouseDown(button="right")
    else:
        raise ValueError("button must be 'left' or 'right'")

    time.sleep(duration)

    pyautogui.mouseUp(button=button)

    return (
        f"completed: {button} click, "
        f"start: ({x}, {y}), "
        f"for {Format_time(duration)}"
    )


def Scroll(direction, startX, startY, duration, speed):
    pyautogui.moveTo(startX, startY)

    if direction not in ("up", "down"):
        raise ValueError("direction must be 'up' or 'down'")

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

    pyautogui.moveTo(startX, startY)
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

    return f"completed: type, text: {string!r}"


def Wait(duration):
    time.sleep(duration)

    return f"completed: wait, for {Format_time(duration)}"


def Done(completed=True):
    return f"completed: {completed}"
