# bot

Tools for behavior-oriented software engineering methodology.

I believe: The way of AI future is not deep learning using like now.

ChatGPT is great,but the problems caused by Explainable AI are still present in ChatGPT.For example, if you find a problem with chatgpt's result, you cannot explore the reasoning with him． And that's not the case with human．All current AI using deep learning have this problem.

I am trying a model that uses symbolic reasoning as the core, simulating human abstraction, analogy and deduction. That is, using Horn-SAT as core and deep learning only for small problems.

I split the job into three parts.

* Enter the workflow of using a software and generate the software code that supports the workflow.
* Generate the usage workflow through natural language.
* Job 1 can generate its own plug-in code and dynamically run it to analyze and learn the content of Job 2.

The whole process is human-like, built on abstraction, analogy and deduction. The Shannon entropy change triggered by each behavior is used as the reward function.

The code here is Job 1. This is a proof-of-principle project, progress will be slow, welcome to communicate with me on related topics.

Some ideas:

* The workflow chart represents how to use the relevant data relationships to achieve a goal, it is the result of the design. The AI design is not covered in Task 1 and is addressed in Task 2.
* At each behavior of the workflow diagram, the software exchanges information with the user. Considering the user as an observer, the higher entropy, the more valuable the software has.If the user is considered as a source, the lower entropy, the more convenient for the user.
* There is a workflow for how to design.This is the hidden goal of Job 2, with built-in support for how to design.
* Once the association with natural language is established, Job 3 will allow the software to self-improve any internal process. This improvement is done either by using natural language to communicate with people or by introspection.

## Getting Started

<!-- TODO: Describe how to prepare to use this project -->

### Installation

```sh
$ make
$ ./bin/install_hooks.sh
```

## Test

```sh
$ make check
$ make test
```

## Requirements

<!-- TODO: Describe stack of this project -->
* [Pipenv](https://github.com/pypa/pipenv) - Dependency management

## Related Documents

<!-- TODO: Insert related documents here-->

## License

<!-- TODO: If you want, set license information here-->
