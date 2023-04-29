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
