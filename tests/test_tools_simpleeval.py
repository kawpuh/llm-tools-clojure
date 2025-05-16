import llm
import json
from llm_tools_simpleeval import simple_eval


def test_simple_eval():
    model = llm.get_model("echo")
    chain_response = model.chain(
        json.dumps(
            {
                "tool_calls": [
                    {"name": "simple_eval", "arguments": {"expression": "3 * 14"}}
                ]
            }
        ),
        tools=[simple_eval],
    )
    responses = list(chain_response.responses())
    tool_results = json.loads(responses[-1].text())["tool_results"]
    assert tool_results == [
        {"name": "simple_eval", "output": "42", "tool_call_id": None}
    ]
