import subprocess
import os

# Step 1: Write the C code to a file
c_code = """
#include <klee/klee.h>
#include <stdio.h>
#include <assert.h>

// Example functions
int example_function1(int x, int y) {
    return (x / 2) + (y / 2) + ((x % 2 + y % 2) / 2);
}

int example_function2(int x, int y) {
    return (int)((x + y) / 2.0);
}

// Comparison function
int compareFunction(int x, int y) {
    int result1 = example_function1(x, y);
    int result2 = example_function2(x, y);
    klee_assert(result1 == result2); // Assertion to check equivalence
    return 1;
}

// Main program
int main() {
    int a, b;

    // Make inputs symbolic
    klee_make_symbolic(&a, sizeof(a), "a");
    klee_make_symbolic(&b, sizeof(b), "b");

    // Call the comparison function
    compareFunction(a, b);

    // Display results
    printf("Symbolic execution complete.\\n");

    return 0;
}
"""

c_file = "symbolic_execution.c"
bc_file = "symbolic_execution.bc"
klee_output_dir = "klee-last"

# Write the C code to a file
with open(c_file, "w") as f:
    f.write(c_code)
print(f"Wrote C code to {c_file}")

# Step 2: Compile the program with KLEE's clang
def compile_program(c_file, bc_file):
    compile_cmd = ["clang", "-emit-llvm", "-c", "-g", c_file, "-o", bc_file]
    try:
        subprocess.run(compile_cmd, check=True)
        print(f"Compiled {c_file} to LLVM bitcode: {bc_file}")
    except subprocess.CalledProcessError as e:
        print("Compilation failed:", e)
        exit(1)

# Step 3: Run KLEE
def run_klee(bc_file):
    klee_cmd = ["klee", bc_file]
    try:
        subprocess.run(klee_cmd, check=True)
        print("KLEE execution completed.")
    except subprocess.CalledProcessError as e:
        print("KLEE execution failed:", e)
        exit(1)

# Step 4: Extract results
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

# Step 5: Clean up KLEE outputs (optional)
def clean_klee_outputs(output_dir):
    if os.path.exists(output_dir):
        for f in os.listdir(output_dir):
            os.remove(os.path.join(output_dir, f))
        os.rmdir(output_dir)
        print(f"Cleaned up {output_dir}")

# Main flow
if __name__ == "__main__":
    # Compile the C program to LLVM bitcode
    compile_program(c_file, bc_file)

    # Run KLEE on the compiled program
    run_klee(bc_file)

    # Extract and display results
    extract_klee_results(klee_output_dir)

    # Uncomment the following line to clean up outputs after execution
    # clean_klee_outputs(klee_output_dir)
