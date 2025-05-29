# llm-tools-clojure

Talk to clojure nREPL as an LLM tool

## Installation

Install this plugin in the same environment as [LLM](https://llm.datasette.io/).
### Local Install
Clone this git repo then run the following
```bash
cd llm-tools-clojure
llm install -e .
```
## Usage
From a directory with a running nrepl instance and .nrepl-port file.
```bash
llm -T ClojureREPL "What functions are there for dealing with the database?" --td
```
