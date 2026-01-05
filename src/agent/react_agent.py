"""Simple ReAct loop example. The LLM is expected to output an Action line like:
Action: count_letters("Strawberry", "r")


We parse the Action, run the tool, then feed Observation back and ask for Final Answer.
"""
import re
from typing import List, Dict
from ..llm_client import LLMClient
from ..tools.count_letters import count_letters


llm = LLMClient()


SYSTEM_PROMPT = """
You are an AI agent using ReAct pattern. When you need to call a tool, output exactly
an Action line in the form:
Action: tool_name("arg1", "arg2")

You can only use below tools:
count_letters(arg1,arg2)




After you see Observation from the environment, produce Final Answer.
Respond in Traditional Chinese.
"""




def parse_action(text: str):
    m = re.search(r"Action:\s*(\w+)\((.*)\)", text)
    if not m:
        return None
    fn = m.group(1)
    args_raw = m.group(2)
    # split on commas not in quotes (simple)
    args = [a.strip().strip('"').strip("'") for a in args_raw.split(',') if a.strip()]
    return fn, args




def run_react(user_input: str):
    messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": user_input}
    ]
    # step 1: ask LLM for Thought + Action
    step1 = llm.generate(messages)
    print("LLM step1:\n", step1)


    action = parse_action(step1)
    print(action)
    if not action:
        
        # no action: return whatever LLM said
        return step1


    fn, args = action
    
    obs = None
    if fn == "count_letters":
        print(f"count_letters {args[0]} {args[1]}")
        obs = count_letters(args[0], args[1])
    else:
        obs = f"Error: unknown tool {fn}"
    

    # feed observation back and ask for final answer
    messages.append({"role": "assistant", "content": step1})
    messages.append({"role": "user", "content": f"Observation: {obs}"})
    print(messages)

    final = llm.generate(messages)
    return final