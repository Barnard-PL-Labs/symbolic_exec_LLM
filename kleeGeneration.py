import re
from openai import OpenAI
import subprocess
import os
from dotenv import load_dotenv
import argparse

# Load environment variables
load_dotenv()

# OpenAI API key setup
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables")
client = OpenAI(api_key=api_key)
model = "gpt-4o"

# Function to make API calls for generating C code
def generate_c_code(prompt):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an assistant that writes C code to solve given problems. Only return the code for the function, no other text. Do not include main or imports."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.5,
        )
        # Remove markdown code block formatting if present
        content = response.choices[0].message.content
        content = content.strip()
        content = content.removeprefix('```c')
        content = content.removeprefix('```')
        content = content.removesuffix('```')
        return content.strip()
    except Exception as e:
        print(f"Error generating code for prompt: {prompt[:30]}... - {e}")
        return None

# Write the C code to a file
def write_c_code_to_file(file_name, functions, compare_code):
    c_code = f"""
#include <klee/klee.h>
#include <stdio.h>
#include <assert.h>

// Generated functions
{functions}

// Comparison function
{compare_code}

// Main program
int main() {{
    int a, b;

    // Make inputs symbolic
    klee_make_symbolic(&a, sizeof(a), "a");
    klee_make_symbolic(&b, sizeof(b), "b");

    // Call the comparison function
    compareFunction(a, b);

    // Display results
    printf("Symbolic execution complete.\\n");

    return 0;
}}
"""
    with open(file_name, "w") as f:
        f.write(c_code)
    print(f"Wrote C code to {file_name}")

# Compile the C program with KLEE's clang
def compile_program(c_file, bc_file):
    compile_cmd = ["clang", "-emit-llvm", "-c", "-g", c_file, "-o", bc_file]
    try:
        subprocess.run(compile_cmd, check=True)
        print(f"Compiled {c_file} to LLVM bitcode: {bc_file}")
    except subprocess.CalledProcessError as e:
        print("Compilation failed:", e)
        exit(1)

# Run KLEE
def run_klee(bc_file):
    klee_cmd = ["klee", bc_file]
    try:
        subprocess.run(klee_cmd, check=True)
        print("KLEE execution completed.")
    except subprocess.CalledProcessError as e:
        print("KLEE execution failed:", e)
        exit(1)

# Extract results
def extract_klee_results(output_dir):
    if not os.path.exists(output_dir):
        print("KLEE output directory not found.")
        return

    print("\nKLEE Results:")
    print("=" * 20)

    # Count generated test cases
    test_case_files = [f for f in os.listdir(output_dir) if f.endswith(".ktest")]
    print(f"Generated test cases: {len(test_case_files)}")

    # Check for assertion failures
    messages_file = os.path.join(output_dir, "messages.txt")
    if os.path.exists(messages_file):
        with open(messages_file, "r") as f:
            messages = f.read()
            if "ASSERTION FAIL" in messages:
                print("\nAssertion Failures Detected:")
                for line in messages.splitlines():
                    if "ASSERTION FAIL" in line:
                        print(line)
            else:
                print("No assertion failures detected.")
    else:
        print("Messages file not found.")

# Generate functions and create a comparison function
def generate_and_run(prompt, c_file, bc_file, klee_output_dir):
    functions = ""
    compare_code = "int compareFunction(int x, int y) {\n"
    numOfGenerations = 3
    for i in range(1, numOfGenerations):
        print(f"Generating function {i}/10")
        c_function = generate_c_code(prompt)
        if c_function:
            function_name = f"example_function{i}"
            c_function = re.sub(r'int \w+\(', f'int {function_name}(', c_function, count=1)
            functions += c_function + "\n\n"
            compare_code += f"    int result{i} = {function_name}(x, y);\n"
    compare_code += "    // Assertions to check equivalence\n"
    for i in range(2, numOfGenerations):
        compare_code += f"    klee_assert(result1 == result{i});\n"
    compare_code += "    return 1;\n}"

    write_c_code_to_file(c_file, functions, compare_code)
    compile_program(c_file, bc_file)
    run_klee(bc_file)
    extract_klee_results(klee_output_dir)

# Main flow
if __name__ == "__main__":
    # Add argument parser
    parser = argparse.ArgumentParser(description='Run KLEE symbolic execution with optional code generation')
    parser.add_argument('--skip-generation', action='store_true', 
                       help='Skip the code generation step and use existing C file')
    parser.add_argument('--prompt', type=str, default="Write a function that computes the greatest common divisor of two integers.",
                       help='Prompt for code generation')
    args = parser.parse_args()

    c_file = "symbolic_execution.c"
    bc_file = "symbolic_execution.bc"
    klee_output_dir = "klee-last"

    if args.skip_generation:
        print("Skipping generation step, using existing C file...")
        compile_program(c_file, bc_file)
        run_klee(bc_file)
        extract_klee_results(klee_output_dir)
    else:
        generate_and_run(args.prompt, c_file, bc_file, klee_output_dir)
