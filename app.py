from flask import Flask, render_template, request
from hypothesis import given, strategies as st
from functools import wraps
import hypothesis.strategies as st
from hypothesis import given
from hypothesis import assume
import string
import unittest
import random
import string
import random
import jsonify
import json

app = Flask(__name__)


# Function to generate sample unit test code for the user's provided function
def generate_sample_test_code(func_name, param_count, expected_result, user_code):
    # Indent the user's code for better formatting
    indented_user_code = '\n'.join(['    ' + line for line in user_code.split('\n')])

    # Create a comma-separated list of argument names
    args_list = ', '.join([f'arg{i}' for i in range(param_count)])

    # Generate the complete test code as a string
    test_code = f"""
import unittest

{indented_user_code}

class Test{func_name}(unittest.TestCase):
    def test_{func_name}(self):
        args = [{args_list}]  # Dynamic user-provided arguments

        # Convert expected result based on return type
        if isinstance(expected_result, str):
            converted_expected_result = expected_result
        elif isinstance(expected_result, int):
            converted_expected_result = int(expected_result)  # Convert to int
        elif isinstance(expected_result, float):
            converted_expected_result = float(expected_result)
        elif isinstance(expected_result, bool):
            converted_expected_result = bool(expected_result)
        else:
            raise ValueError("Unsupported return type")

        self.assertEqual({func_name}({args_list}), converted_expected_result)

if __name__ == "__main__":
    unittest.main()
"""

    return test_code


def run_unit_test(function, return_type, expected_result, param_count, args_list, param_types):
    class DynamicTestCase(unittest.TestCase):
        def test_dynamic(self):
            # Convert argument values to the appropriate types
            args = []

            for i in range(param_count):
                param_type = param_types[i]
                param_value = args_list[i]

                if param_type == "int":
                    args.append(int(param_value))
                elif param_type == "float":
                    args.append(float(param_value))
                elif param_type == "bool":
                    args.append(param_value.lower() == "true")
                elif param_type == "str":
                    args.append(str(param_value))
                elif param_type == "list":
                    # Convert the parameter value to a list of integers (comma-separated values)
                    list_values = [int(val) for val in param_value.split(',')]
                    args.append(list_values)
                else:
                    args.append(param_value)

            # Convert the expected result based on the specified return type
            if return_type == "int":
                converted_expected_result = int(expected_result)
            elif return_type == "float":
                converted_expected_result = float(expected_result)
            elif return_type == "bool":
                converted_expected_result = expected_result.lower() == "true"
            elif return_type == "str":
                converted_expected_result = str(expected_result)
            elif return_type == "list":
                # Convert the expected result to a list (comma-separated values)
                converted_expected_result = expected_result.split(',')
            else:
                converted_expected_result = str(expected_result)

            # Run the user's function with the provided arguments and assert the result
            print("Arguments:", args)
            print("Expected Result:", converted_expected_result)

            # Run the user's function with the provided arguments and assert the result
            actual_result = function(*args)
            print("Actual Result:", actual_result)

            self.assertEqual(actual_result, converted_expected_result)
            self.assertEqual(function(*args), converted_expected_result)

    suite = unittest.TestLoader().loadTestsFromTestCase(DynamicTestCase)
    test_result = unittest.TextTestRunner(verbosity=2).run(suite)

    return f"Passed\n{test_result}" if test_result.wasSuccessful() else f"Failed\n{test_result}"


# Function to execute property-based random testing
def execute_property_based_test(user_code, param_count):
    # Define a property-based test
    @given(*[st.floats(allow_nan=False, allow_infinity=False)] * param_count)
    def property_based_test(*args):
        try:
            # Execute the user's code with the generated inputs
            exec(user_code, globals(), {'args': args})
        except Exception as e:
            return ("Error", str(e))
        return None  # No assertion failure, return None

    # Run the property-based test
    test_result = property_based_test()

    if test_result is None:
        return "All property-based tests passed!"
    else:
        return f"Test Result: {test_result[0]}, Message: {test_result[1]}"


def dynamic_given(num_params):
    def decorator(func):
        @given(*[st.floats(allow_nan=False, allow_infinity=False)] * num_params)
        @wraps(func)
        def wrapper(*args):
            return func(*args)

        return wrapper

    return decorator


app = Flask(__name__)


def execute_property_based_test(user_function, param_count, num_tests, min_value, max_value, data_type):
    results = []

    for test_num in range(1, num_tests + 1):
        try:
            # Generate random arguments based on param_count and the specified range
            args = [random.uniform(min_value, max_value) for _ in range(param_count)]

            # Generate a random assumed result within the specified range based on data_type
            if data_type == "int":
                assumed_result = random.randint(int(min_value), int(max_value))
            elif data_type == "float":
                assumed_result = random.uniform(min_value, max_value)
            elif data_type == "bool":
                assumed_result = random.choice([True, False])
            elif data_type == "str":
                assumed_result = ''.join(
                    random.choice(string.ascii_letters) for _ in range(random.randint(int(min_value), int(max_value))))
            else:
                assumed_result = None  # Invalid data type

            # Call the user's function with the generated arguments
            if data_type == "int":
                actual_result = int(user_function(*args))
            elif data_type == "str":
                actual_result = str(user_function(*args))
            elif data_type == "bool":
                actual_result = bool(user_function(*args))
            elif data_type == "float":
                actual_result = float(user_function(*args))

            # Check if the actual result matches the assumed result
            if data_type == "bool":
                status = "Passed" if actual_result == assumed_result else "Failed"
            elif data_type == "str":
                status = "Passed" if actual_result == assumed_result else "Failed"
            elif data_type == "int":
                status = "Passed " if actual_result == assumed_result else "Failed"
            else:
                if abs(actual_result - assumed_result) < 0.01:
                    status = "Passed"
                else:
                    status = "Failed"

            # Append the results for this test
            results.append({
                "Test": test_num,
                "Assumed": assumed_result,
                "Actual": actual_result,
                "Status": status
            })

        except Exception as e:
            # If an exception occurred, mark the test as failed
            results.append({
                "Test": test_num,
                "Assumed": None,
                "Actual": None,
                "Status": f"Failed (Error: {str(e)})"
            })

    return results


# Define a Flask route for the index page
@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    generated_test_code = None

    if request.method == "POST":
        code = request.form.get("input_function")
        func_name = request.form.get("func_name")
        return_type = request.form.get("return_type")
        param_count = int(request.form.get("param_count"))
        expected_result = request.form.get("expected_result")

        args_list = [request.form.get(f'param_{i}') for i in range(param_count)]
        param_types = [request.form.get(f'param_{i}_type') for i in range(param_count)]

        user_code = f"{code}\n"

        exec(user_code, globals())

        if func_name in globals() and callable(globals()[func_name]):
            function = globals()[func_name]

            test_code = generate_sample_test_code(func_name, param_count, expected_result, user_code)
            generated_test_code = test_code

            test_result = run_unit_test(function, return_type, expected_result, param_count, args_list, param_types)
            result = f"Test Result: {test_result}"

    return render_template("index.html", result=result, generated_test_code=generated_test_code)


# Modify the /random_test.html route for property-based random testing
@app.route('/random_test.html', methods=["GET", "POST"])
def random_test():
    results = []

    if request.method == "POST":
        user_code = request.form.get("user_code")
        param_count = int(request.form.get("param_count"))
        num_tests = int(request.form.get("num_tests"))
        min_value = float(request.form.get("min_value"))
        max_value = float(request.form.get("max_value"))
        data_type = request.form.get("data_type")  # Retrieve the selected data type from the form
        func_name = request.form.get("func_name")

        # Define a dictionary to hold the user's function
        user_function_dict = {}

        try:
            # Execute the user's code and capture the user's function
            exec(user_code, user_function_dict)

            # Check if the user's function is callable
            if callable(user_function_dict.get(func_name)):
                user_function = user_function_dict[func_name]

                # Perform random testing the specified number of times
                results = execute_property_based_test(user_function, param_count, num_tests, min_value, max_value,
                                                      data_type)
            else:
                results.append({
                    "Test": 1,
                    "Assumed": None,
                    "Actual": None,
                    "Status": "Failed (The provided code does not define a callable function 'user_function')."
                })

        except Exception as e:
            results.append({
                "Test": 1,
                "Assumed": None,
                "Actual": None,
                "Status": f"Failed (Error: {str(e)})"
            })

    return render_template("random_test.html", results=results)


@app.route("/api/function_test", methods=["POST"])
def function_test():
    # Retrieve user input from the JSON request body
    request_data = request.get_json()
    code = request_data.get("input_function")
    func_name = request_data.get("func_name")
    return_type = request_data.get("return_type")
    param_count = int(request_data.get("param_count"))
    expected_result = request_data.get("expected_result")
    args_list = request_data.get("args_list")

    # Combine the user-provided code into a single string
    user_code = f"{code}\n"

    # Execute the user's code in the global namespace
    exec(user_code, globals())

    # Check if the specified function is callable in the global namespace
    if func_name in globals() and callable(globals()[func_name]):
        function = globals()[func_name]

        # Run the unit test and get the test result ("Passed" or "Failed")
        test_result = run_unit_test(function, return_type, expected_result, param_count, args_list)

        # Return the test result as JSON
        response_data = {"test_result": test_result}
        return jsonify(response_data)


@app.route("/api/random_test", methods=["POST"])
def random_test_api():
    try:
        # Parse the JSON data from the POST request
        data = request.get_json()

        # Extract the user's Python code and testing parameters
        user_code = data.get("user_code")
        func_name = data.get("func_name")
        param_count = int(data.get("param_count"))
        num_tests = int(data.get("num_tests"))
        min_value = float(data.get("min_value"))
        max_value = float(data.get("max_value"))
        data_type = data.get("data_type")

        # Define a dictionary to hold the user's function
        # user_function_dict = {}
        user_code = f"{user_code}\n"

        # Execute the user's code and capture the user's function
        exec(user_code, globals())

        # Check if the user's function is callable
        # Check if the user's function is callable
        if func_name in globals() and callable(globals()[func_name]):
            user_function = globals()[func_name]

            # Perform random testing the specified number of times
            results = execute_property_based_test(user_function, param_count, num_tests, min_value, max_value,
                                                  data_type)

            # Prepare the results as JSON
            response = {
                "message": "Random testing completed successfully",
                "results": results
            }

            return jsonify(response), 200
        else:
            response = {
                "error": "The provided code does not define a callable function 'user_function'"
            }
            return jsonify(response), 400

    except Exception as e:
        response = {
            "error": f"An error occurred: {str(e)}"
        }
        return jsonify(response), 500


# Run the Flask application
if __name__ == "__main__":
    app.run(debug=True)
