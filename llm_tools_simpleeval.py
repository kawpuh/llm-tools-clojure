import llm
from simpleeval import simple_eval


@llm.hookimpl
def register_tools(register):
    register(simple_eval)
