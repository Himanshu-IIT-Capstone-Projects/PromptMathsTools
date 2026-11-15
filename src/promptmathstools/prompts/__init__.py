'''
from .role_and_chat import ROLE_SYSTEM_PROMPT
from .chain_of_thought import COT_INSTRUCTIONS
from .few_shot import get_few_shot_prompt
from .structured_classifier import classify_problem

ALL_PROMPTS = {
    "role_and_chat": ROLE_SYSTEM_PROMPT,    
    "chain_of_thought": COT_INSTRUCTIONS,
    "few_shot": get_few_shot_prompt,
    "structured_classifier": classify_problem
}

'''