# symbolic_exec_LLM

### Getting started

Start the klee container

```docker run --rm -it -v $(pwd):/home/klee/workspace klee/klee```

Install the python dependencies
TODO: Add to dockerfile

```pip install openai```
```pip install python-dotenv```

### To run automatically

Run the python script to generate the C code and check equivalence with symbolic execution
```python kleeGeneration.py```

### To run by hand

Compile the C code to a bytecode file

```clang -emit-llvm -c -g kleeTest.c -o kleeTest.bc```

Run the symbolic execution

```klee --write-smt2s kleeTest.bc```