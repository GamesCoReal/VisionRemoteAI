import controls
import ast


# ============================================================
# FUNCTIONS THE AI IS ALLOWED TO EXECUTE
# ============================================================

ALLOWED_FUNCTIONS = {
    "click": controls.click,
    "scroll": controls.scroll,
    "move": controls.move,
    "type": controls.type,
    "wait": controls.wait,
    "screen": controls.screen,
    "done": controls.done,
    "search": controls.search,
    "help": controls.help,
}


# ============================================================
# PARSE A COMMAND
# ============================================================

def parse_command(command):
    tree = ast.parse(
        command.lower().strip(),
        mode="eval"
    )

    if not isinstance(tree.body, ast.Call):
        raise ValueError("Not a function call.")

    call = tree.body

    if not isinstance(call.func, ast.Name):
        raise ValueError("Invalid function.")

    function_name = call.func.id.lower()

    if function_name not in ALLOWED_FUNCTIONS:
        raise ValueError(
            f"Function '{call.func.id}' is not allowed."
        )

    if call.keywords:
        raise ValueError(
            "Keyword arguments are not allowed."
        )

    arguments = []

    for argument in call.args:

        if isinstance(argument, ast.Constant):
            arguments.append(argument.value)

        elif isinstance(argument, ast.Name):
            arguments.append(argument.id)

        else:
            arguments.append(
                ast.literal_eval(argument)
            )

    return function_name, arguments

# ============================================================
# EXECUTE A COMMAND
# ============================================================

def execute_command(command):
    try:
        function_name, arguments = parse_command(command)

        function = ALLOWED_FUNCTIONS[function_name]

        result = function(*arguments)

        return function_name, result

    except Exception as error:
        return None, f"ERROR: {error}"


# ============================================================
# CHECK IF COMMAND IS DONE()
# ============================================================

def check_done(function_name):
    return function_name == "done"


# ============================================================
# MAIN
# ============================================================

while True:

    print()
    print("=" * 60)
    print("VisualRemoteAI")
    print("=" * 60)

    user_request = input("\nUSER:\n> ").strip()

    if not user_request:
        continue

    print()
    print("Ann:")
    print("PLAN:")

    # --------------------------------------------------------
    # TEMPORARY MANUAL AI INPUT
    #
    # Later this will be replaced by the actual local AI.
    # --------------------------------------------------------

    while True:

        print()
        ai_response = input("ANN:\n> ").strip()

        if not ai_response:
            continue

        # ----------------------------------------------------
        # Try to parse the AI's command
        # ----------------------------------------------------

        try:
            function_name, arguments = parse_command(
                ai_response
            )

        except Exception:

            # Anything that isn't a valid function call
            # is treated as something the AI is saying.

            print()
            print("Ann:")
            print(ai_response)

            continue

        # ----------------------------------------------------
        # Show the command being executed
        # ----------------------------------------------------

        print()
        print("EXECUTE:")
        print(ai_response)

        # ----------------------------------------------------
        # Execute the command
        # ----------------------------------------------------

        executed_function, result = execute_command(
            ai_response
        )

        print()
        print(result)

        # ----------------------------------------------------
        # DONE = STOP EVERYTHING
        # ----------------------------------------------------

        if check_done(executed_function):

            print()
            print("Ann:")
            print("TASK FINISHED.")

            break

        # ----------------------------------------------------
        # SCREEN ALREADY SHOWS THE SCREEN
        # ----------------------------------------------------

        if executed_function == "screen":
            continue

        # ----------------------------------------------------
        # AUTOMATIC SCREEN VIEW AFTER EVERY ACTION
        # ----------------------------------------------------

        print()
        print("Ann:")
        print("VIEWING SCREEN...")

        try:
            controls.screen()

        except Exception as error:

            print()
            print(
                f"ERROR VIEWING SCREEN: {error}"
            )
