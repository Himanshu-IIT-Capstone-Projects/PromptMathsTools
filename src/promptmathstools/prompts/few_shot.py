# prompts/02_few_shot.py
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate

FEW_SHOT_EXAMPLES = [
    {
        "input": "2kg mangoes cost 200 rupees. I bought 500gm and paid with 500 rupees. Balance?",
        "output": (
            "Step 1: Convert 500gm to 0.5kg.\n"
            "Step 2: Find price per kg -> call divide(200, 2).\n"
            "Step 3: Find cost of 0.5kg -> call multiply(100, 0.5).\n"
            "Step 4: Find remaining money -> call subtract(500, 50)."
        ),
    },
    {
        "input": "Find x for (x + 2)*(x - 3) = 0",
        "output": "Step 1: Identify quadratic expression.\nStep 2: Call solve_quadratic('(x + 2)*(x - 3)').",
    },
]

def get_few_shot_prompt() -> FewShotChatMessagePromptTemplate:
    print("\n [get_few_shot_prompt()] started")
    try:
        example_template = ChatPromptTemplate.from_messages([
            ("human", "{input}"),
            ("ai", "{output}"),
        ])
        return FewShotChatMessagePromptTemplate(
            example_prompt=example_template,
            examples=FEW_SHOT_EXAMPLES,
        )
    except Exception as error:
        print(f"\n [get_few_shot_prompt()] error: {error!r}")
        raise
    finally:
        print("\n [get_few_shot_prompt()] ended")
