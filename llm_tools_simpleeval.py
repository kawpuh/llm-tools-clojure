import llm
from simpleeval import simple_eval as _simple_eval


def simple_eval(expression: str) -> str:
    """
    Evaluate a simple expression using the simpleeval library.
    """
    try:
        result = _simple_eval(expression)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"


@llm.hookimpl
def register_tools(register):
    register(simple_eval)
