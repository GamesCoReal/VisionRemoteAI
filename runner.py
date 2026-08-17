import controls
import ast


# Functions the AI is allowed to execute
ALLOWED_FUNCTIONS = {
    "Click": controls.Click,
    "Scroll": controls.Scroll,
    "Swipe": controls.Swipe,
    "Type": controls.Type,
    "Wait": controls.Wait,
    "Done": controls.Done
}


def execute_command(command):
    try:
        tree = ast.parse(command.strip(), mode="eval")

        if not isinstance(tree.body, ast.Call):
            return "ERROR: Not a function call."

        call = tree.body

        if not isinstance(call.func, ast.Name):
            return "ERROR: Invalid function."

        function_name = call.func.id

        if function_name not in ALLOWED_FUNCTIONS:
            return f"ERROR: Function '{function_name}' is not allowed."

        if call.keywords:
            return "ERROR: Keyword arguments are not allowed."

        arguments = [
            ast.literal_eval(argument)
            for argument in call.args
        ]

        function = ALLOWED_FUNCTIONS[function_name]

        return function(*arguments)

    except Exception as error:
        return f"ERROR: {error}"


def check_done(command):
    try:
        tree = ast.parse(command.strip(), mode="eval")

        if not isinstance(tree.body, ast.Call):
            return False

        if not isinstance(tree.body.func, ast.Name):
            return False

        if tree.body.func.id != "Done":
            return False

        return True

    except Exception:
        return False


while True:

    print()
    print("=" * 60)
    print("VisualRemoteAI")
    print("=" * 60)

    user_request = input("\nUSER:\n> ")

    print()
    print("Ann:")
    print("PLAN:")

    # For now, you type everything the AI would say.
    # Later, this input will be replaced by the actual AI.

    while True:

        print()
        ai_response = input("ANN:\n> ").strip()

        if not ai_response:
            continue

        # If the AI says Done(), execute it and stop this task.
        if check_done(ai_response):

            print()
            print("EXECUTE:")
            print(ai_response)

            result = execute_command(ai_response)

            print()
            print(result)

            break

        # Try to determine whether the AI response is a
        # control function such as Click(), Scroll(), etc.
        try:
            tree = ast.parse(ai_response, mode="eval")

            if (
                isinstance(tree.body, ast.Call)
                and isinstance(tree.body.func, ast.Name)
                and tree.body.func.id in ALLOWED_FUNCTIONS
            ):

                print()
                print("EXECUTE:")
                print(ai_response)

                result = execute_command(ai_response)

                print()
                print(result)

                print()
                print("Ann:")
                print("VIEWING SCREEN...")

            else:
                # Anything that isn't a control function is
                # simply treated as something the AI is saying.
                print()
                print("Ann:")
                print(ai_response)

        except Exception:
            print()
            print("Ann:")
            print(ai_response)
