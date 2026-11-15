from langchain.agents import create_agent
from langgraph.graph.state import CompiledStateGraph
# prompts 
from promptmathstools.prompts.chain_of_thought import COT_INSTRUCTIONS
from promptmathstools.prompts.few_shot import get_few_shot_prompt
from promptmathstools.prompts.role_and_chat import ROLE_SYSTEM_PROMPT
# utility
from promptmathstools.tools import ALL_MATH_TOOLS
from promptmathstools.utility.loadllm import load_llm


def build_math_agent() -> CompiledStateGraph:
    print("\n [build_math_agent()] started")
    try:
        llm = load_llm()

        few_shot_messages = get_few_shot_prompt().format_messages()
        examples_text = "\n".join(
            f"{m.type.upper()}: {m.content}" for m in few_shot_messages)
        
        system_instructions = (
            f"{ROLE_SYSTEM_PROMPT}\n\n"
            f"{COT_INSTRUCTIONS}\n\n"
            f"EXAMPLES:\n{examples_text}"
            )
        
        return create_agent(
            model=llm,
            tools=ALL_MATH_TOOLS,
            system_prompt=system_instructions,
            name="AgentExecutor",
        )
    except Exception as error:
        print(f"\n [build_math_agent()] error: {error!r}")
        raise
    finally:
        print("\n [build_math_agent()] ended")
