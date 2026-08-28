import requests
import pyautogui
import base64
import io
import json


MODEL = "qwen3.5:2b"
OLLAMA_URL = "http://localhost:11434/api/chat"


SYSTEM_PROMPT = """
You are Ann, a visual computer assistant.

You receive:
1. A user's goal.
2. A screenshot of the user's computer.

You can SEE the screenshot, but you currently have NO ability
to control the computer.

Your job is to plan how the user's goal could be accomplished.

IMPORTANT:

- Use the screenshot as the source of truth.
- Do not invent UI elements.
- Do not assume an application, button, icon, window, folder,
  shortcut, or menu exists unless it is visible.
- Do not claim that you performed an action.
- Do not control the computer.
- Do not provide hidden reasoning.
- Do not repeatedly second-guess yourself.
- Be concise.

When choosing coordinates:

- Coordinates must refer to the screenshot you receive.
- x increases from left to right.
- y increases from top to bottom.
- For a clickable object, choose a point near the CENTER of it.
- Never guess coordinates for something that cannot be seen.
- Include what the coordinates are intended to point at.

CURRENTLY:

You are ONLY planning.

Do not execute anything.

IMPORTANT:AVAILABLE FUNCTIONS:

search(context)

Use search(context) when you need to find or open an application,
website, file, setting, or other searchable item.

The search function automatically uses the operating system's
built-in search feature.

Examples:

search("Google")
search("Canva")
search("Calculator")

IMPORTANT:

- You ARE allowed to use search().
- Prefer search() when looking for an application or other item
  that can reasonably be found through system search.
- Do NOT invent coordinates for opening an application when
  search() can be used instead.
- After using search(), a new screenshot will be provided so you
  can see the search results.
"""


def get_screen_image():

    screenshot = pyautogui.screenshot()

    screen_width, screen_height = screenshot.size

    resize_width = screen_width // 2
    resize_height = screen_height // 2

    screenshot = screenshot.resize(
        (
            resize_width,
            resize_height
        )
    )

    image_buffer = io.BytesIO()

    screenshot.save(
        image_buffer,
        format="JPEG",
        quality=70
    )

    image_data = base64.b64encode(
        image_buffer.getvalue()
    ).decode("utf-8")

    return (
        image_data,
        screen_width,
        screen_height,
        resize_width,
        resize_height
    )


def ask_ai(prompt, image_data):

    response = requests.post(
        OLLAMA_URL,

        json={
            "model": MODEL,

            "messages": [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },

                {
                    "role": "user",
                    "content": prompt,
                    "images": [
                        image_data
                    ]
                }
            ],

            "stream": False,

            "think": False,

            "options": {
                "temperature": 0.2,
                "num_predict": 200
            }
        },

        timeout=300
    )

    response.raise_for_status()

    return response.json()["message"]["content"].strip()


# ============================================================
# JSON PARSER
# Allows Ann to return normal JSON OR JSON inside ```json blocks.
# ============================================================

def parse_json(response):

    response = response.strip()

    # Remove Markdown code fences.
    if response.startswith("```"):

        lines = response.splitlines()

        # Remove first line:
        # ```json
        # or
        # ```
        if lines:
            lines = lines[1:]

        # Remove final ```
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        response = "\n".join(lines).strip()

    return json.loads(response)


def make_plan(goal, image_data):

    prompt = f"""
Goal:

{goal}

Look at the screenshot.

Create the shortest realistic high-level plan.

Return ONLY valid JSON:

{{
    "plan": [
        "step 1",
        "step 2"
    ]
}}

Maximum 5 steps.

Use fewer when possible.

No explanations.
"""

    response = ask_ai(
        prompt,
        image_data
    )

    try:

        return parse_json(response)

    except json.JSONDecodeError:

        print()
        print("ANN RETURNED INVALID PLAN:")
        print(response)

        return None


def split_step(
    goal,
    major_step,
    image_data,
    resize_width,
    resize_height
):

    prompt = f"""
Goal:

{goal}

Current major step:

{major_step}

The screenshot you are viewing is:

{resize_width} pixels wide
{resize_height} pixels high

Break ONLY this major step into the smallest realistic
actions needed to accomplish it.

For every mouse action, provide the coordinates on the
screenshot.

Return ONLY valid JSON.

Example:

{{
    "actions": [
        {{
            "action": "click",
            "button": "left",
            "x": 25,
            "y": 520,
            "duration": 0.1,
            "amount": 1,
            "target": "Start button"
        }}
    ]
}}

Possible action types for now:

click
move
scroll
type
wait

For click:

{{
    "action": "click",
    "button": "left",
    "x": 100,
    "y": 200,
    "duration": 0.1,
    "amount": 1,
    "target": "description of what is being clicked"
}}

For move:

{{
    "action": "move",
    "startX": 100,
    "startY": 200,
    "endX": 300,
    "endY": 200,
    "target": "description of what is being moved"
}}

For scroll:

{{
    "action": "scroll",
    "direction": "down",
    "startX": 500,
    "startY": 400,
    "duration": 1,
    "speed": 5,
    "target": "description"
}}

For type:

{{
    "action": "type",
    "text": "google"
}}

For wait:

{{
    "action": "wait",
    "duration": 2
}}

Use AT MOST 5 actions.

Use fewer when possible.

Coordinates MUST be inside the screenshot.

Do not invent coordinates.

Do not execute anything.
"""

    response = ask_ai(
        prompt,
        image_data
    )

    try:

        return parse_json(response)

    except json.JSONDecodeError:

        print()
        print("ANN RETURNED INVALID ACTION PLAN:")
        print(response)

        return None


def convert_coordinates(
    x,
    y,
    resize_width,
    resize_height,
    screen_width,
    screen_height
):

    real_x = round(
        x * screen_width / resize_width
    )

    real_y = round(
        y * screen_height / resize_height
    )

    real_x = max(
        0,
        min(real_x, screen_width - 1)
    )

    real_y = max(
        0,
        min(real_y, screen_height - 1)
    )

    return real_x, real_y


# ============================================================
# MAIN PROGRAM
# ============================================================

print("=" * 60)
print("VisualRemoteAI")
print("=" * 60)


while True:

    goal = input(
        "\nGOAL:\n> "
    ).strip()

    if not goal:
        continue

    if goal.lower() in (
        "exit",
        "quit",
        "stop"
    ):
        break


    # ========================================================
    # SCREENSHOT
    # ========================================================

    print()
    print("📸 CAPTURING SCREEN...")

    (
        image_data,
        screen_width,
        screen_height,
        resize_width,
        resize_height
    ) = get_screen_image()


    # ========================================================
    # HIGH LEVEL PLAN
    # ========================================================

    print()
    print("🧠 CREATING PLAN...")

    plan_data = make_plan(
        goal,
        image_data
    )

    if not plan_data:
        continue


    plan = plan_data.get(
        "plan",
        []
    )


    print()
    print("ANN:")
    print("PLAN:")

    for number, step in enumerate(
        plan,
        1
    ):

        print(
            f"{number}. {step}"
        )


    if not plan:

        print(
            "No plan was created."
        )

        continue


    # ========================================================
    # FIRST MAJOR STEP
    # ========================================================

    print()
    print("=" * 60)
    print("CURRENT STEP")
    print("=" * 60)

    current_step = plan[0]

    print()
    print(
        f"STEP 1: {current_step}"
    )


    # ========================================================
    # NEW SCREENSHOT
    # ========================================================

    print()
    print("📸 ANALYZING CURRENT SCREEN...")

    (
        image_data,
        screen_width,
        screen_height,
        resize_width,
        resize_height
    ) = get_screen_image()


    # ========================================================
    # SPLIT STEP INTO ACTIONS
    # ========================================================

    actions_data = split_step(
        goal,
        current_step,
        image_data,
        resize_width,
        resize_height
    )

    if not actions_data:
        continue


    actions = actions_data.get(
        "actions",
        []
    )


    print()
    print("ANN:")
    print("ACTIONS:")


    # ========================================================
    # DISPLAY ACTIONS + REAL COORDINATES
    # ========================================================

    for number, action in enumerate(
        actions,
        1
    ):

        print()
        print(
            f"{number}. {action}"
        )


        # ----------------------------------------------------
        # CLICK
        # ----------------------------------------------------

        if action.get("action") == "click":

            x = action.get("x")
            y = action.get("y")

            if x is not None and y is not None:

                real_x, real_y = convert_coordinates(
                    x,
                    y,
                    resize_width,
                    resize_height,
                    screen_width,
                    screen_height
                )

                print(
                    f"   AI coordinates: "
                    f"({x}, {y})"
                )

                print(
                    f"   REAL coordinates: "
                    f"({real_x}, {real_y})"
                )

                print(
                    f"   TARGET: "
                    f"{action.get('target', 'unknown')}"
                )


        # ----------------------------------------------------
        # MOVE
        # ----------------------------------------------------

        elif action.get("action") == "move":

            start_x = action.get("startX")
            start_y = action.get("startY")
            end_x = action.get("endX")
            end_y = action.get("endY")

            if None not in (
                start_x,
                start_y,
                end_x,
                end_y
            ):

                (
                    real_start_x,
                    real_start_y
                ) = convert_coordinates(
                    start_x,
                    start_y,
                    resize_width,
                    resize_height,
                    screen_width,
                    screen_height
                )

                (
                    real_end_x,
                    real_end_y
                ) = convert_coordinates(
                    end_x,
                    end_y,
                    resize_width,
                    resize_height,
                    screen_width,
                    screen_height
                )

                print(
                    f"   AI start: "
                    f"({start_x}, {start_y})"
                )

                print(
                    f"   REAL start: "
                    f"({real_start_x}, {real_start_y})"
                )

                print(
                    f"   AI end: "
                    f"({end_x}, {end_y})"
                )

                print(
                    f"   REAL end: "
                    f"({real_end_x}, {real_end_y})"
                )


        # ----------------------------------------------------
        # OTHER ACTIONS
        # ----------------------------------------------------

        elif action.get("action") == "scroll":

            print(
                f"   TARGET: "
                f"{action.get('target', 'unknown')}"
            )


        elif action.get("action") == "type":

            print(
                f"   TEXT: "
                f"{action.get('text', '')!r}"
            )


        elif action.get("action") == "wait":

            print(
                f"   DURATION: "
                f"{action.get('duration', 0)} seconds"
            )


    # ========================================================
    # END
    # ========================================================

    print()
    print("=" * 60)
    print("COORDINATE TEST COMPLETE")
    print("=" * 60)