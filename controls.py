import pyautogui
import time
import math
import random
import platform

from rich.console import Console
from rich_pixels import Pixels


console = Console()


def format_time(seconds):
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


def screen():
    screenshot = pyautogui.screenshot()

    screen_width, screen_height = pyautogui.size()

    resize_width = screen_width // 10
    resize_height = screen_height // 10

    console.print(
        Pixels.from_image(
            screenshot,
            resize=(resize_width, resize_height)
        )
    )


def human_move(x, y):
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

    full_screen_time = random.uniform(1.7, 2.3)

    duration = (
        distance / screen_diagonal
    ) * full_screen_time

    pyautogui.moveTo(
        x,
        y,
        duration=duration
    )

    return (
        f"completed: mouse move, "
        f"start: ({start_x}, {start_y}), "
        f"end: ({x}, {y}), "
        f"for {format_time(duration)}"
    )


def search(context):

    os = platform.system().lower()

    if os == "windows":
        pyautogui.press("win")
        time.sleep(0.2)
        pyautogui.write(context)

    elif os == "darwin":
        pyautogui.hotkey("command", "space")
        time.sleep(0.2)
        pyautogui.write(context)

    elif os == "linux":
        # Linux depends on the desktop environment
        ...

    else:
        raise ValueError(
            f"unsupported operating system: {os}"
        )


def click(button, x, y, duration, amount):
    button = str(button).strip().lower()

    human_move(x, y)

    for _ in range(amount):
        pyautogui.mouseDown(button=button)

        time.sleep(duration)

        pyautogui.mouseUp(button=button)

        if _ < amount - 1:
            time.sleep(0.05)

    return (
        f"completed: {button} click, "
        f"start: ({x}, {y}), "
        f"for {format_time(duration)}, "
        f"amount: {amount}"
    )


def scroll(direction, startX, startY, duration, speed):
    direction = str(direction).strip().lower()

    human_move(startX, startY)

    speed = speed if direction == "up" else -speed

    start_time = time.time()

    while time.time() - start_time < duration:
        pyautogui.scroll(speed)
        time.sleep(0.05)

    return (
        f"completed: scroll {direction}, "
        f"start: ({startX}, {startY}), "
        f"for {format_time(duration)}, "
        f"speed: {abs(speed)}"
    )


def move(startX, startY, endX, endY):
    human_move(startX, startY)

    pyautogui.dragTo(
        endX,
        endY,
        duration=0.5
    )

    return (
        f"completed: move, "
        f"start: ({startX}, {startY}), "
        f"end: ({endX}, {endY})"
    )


def type(text):
    pyautogui.write(text)

    return (
        f"completed: type, "
        f"text: {text!r}"
    )


def wait(duration):
    time.sleep(duration)

    return (
        f"completed: wait, "
        f"for {format_time(duration)}"
    )


def done(completed=True):
    return f"completed: {completed}"


def help(function=None):

    functions = {

        "click": {
            "description": "Use to press a location on the device. The pointer moves to the location first.",
            "usage": "click(left/right, x, y, duration, amount)",
            "parameters": {
                "button": "Use left or right.",
                "x": "Horizontal screen coordinate.",
                "y": "Vertical screen coordinate.",
                "duration": "How long to hold each click, in seconds.",
                "amount": "How many times to click."
            },
            "example": "click(left, 500, 400, 0.1, 2)"
        },

        "scroll": {
            "description": "Use to scroll content vertically up or down.",
            "usage": "scroll(up/down, startX, startY, duration, speed)",
            "parameters": {
                "direction": "Use up or down.",
                "startX": "Horizontal screen coordinate where scrolling begins.",
                "startY": "Vertical screen coordinate where scrolling begins.",
                "duration": "How long to scroll, in seconds.",
                "speed": "How much to scroll each time."
            },
            "example": "scroll(down, 500, 400, 1, 5)"
        },

        "move": {
            "description": "Use to move from one location to another while holding the pointer/button down. This can be used to drag an object or perform a swipe-like gesture.",
            "usage": "move(startX, startY, endX, endY)",
            "parameters": {
                "startX": "Horizontal screen coordinate where the movement begins.",
                "startY": "Vertical screen coordinate where the movement begins.",
                "endX": "Horizontal screen coordinate where the movement ends.",
                "endY": "Vertical screen coordinate where the movement ends."
            },
            "example": "move(500, 700, 500, 300)"
        },

        "type": {
            "description": "Use to type text into the currently selected input or location. Text capitalization is preserved.",
            "usage": "type(text)",
            "parameters": {
                "text": "The exact text you want the device to type."
            },
            "example": "type(Hello World)"
        },

        "wait": {
            "description": "Use to pause before performing the next action, such as while waiting for a page or application to load.",
            "usage": "wait(duration)",
            "parameters": {
                "duration": "How long to wait, in seconds."
            },
            "example": "wait(2)"
        },

        "screen": {
            "description": "Use to view the current screen of the device.",
            "usage": "screen()",
            "parameters": {},
            "example": "screen()"
        },

        "done": {
            "description": "Use to stop controlling the device. True means the task was completed successfully. False means the task could not be completed.",
            "usage": "done(completed)",
            "parameters": {
                "completed": "Use True when the task is completed or False when it cannot be completed."
            },
            "example": "done(True)"
        },
	
	"search": {
	    "usage": "search(context)",
	    "parameters": {
	        "context": "What you want to search for."
	    },
	    "example": "search(Canva)",
	    "description": "Uses the operating system's search feature to find or launch something."
	},

        "help": {
            "description": "Use to learn what functions are available or how to use a specific function.",
            "usage": "help() or help(function)",
            "parameters": {
                "function": "The name of the function you want information about. Leave empty to see all available functions."
            },
            "example": "help(click)"
        }
    }

    if function is None:
        return list(functions.keys())

    function = str(function).strip().lower()

    for name in functions:
        if name.lower() == function:
            return functions[name]

    return (
        f"Unknown function: {function}\n"
        f"Available functions: {list(functions.keys())}"
    )
