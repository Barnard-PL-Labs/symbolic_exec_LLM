# symbolic_exec_LLM

This is a project to generate C code using an LLM and check its equivalence with symbolic execution.

Note: Floating point operations are not supported by KLEE, and so we kind of have to avoid them. Not ideal...


### Getting started

Start the klee container

```docker run --rm -it -v $(pwd):/home/klee/workspace klee/klee```

Install the python dependencies
TODO: Add to dockerfile

```pip install openai python-dotenv```

### To run automatically

Run the python script to generate the C code and check equivalence with symbolic execution
```python3 kleeGeneration.py```

### To run by hand

Compile the C code to a bytecode file

```clang -emit-llvm -c -g kleeTest.c -o kleeTest.bc```

Run the symbolic execution

```klee --write-smt2s kleeTest.bc```