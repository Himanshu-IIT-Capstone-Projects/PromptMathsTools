# prompts/03_chain_of_thought.py
COT_INSTRUCTIONS = (
    "Follow Chain-of-Thought reasoning strictly:\n"
    "1. Identify known values and convert units (e.g., grams to kilograms) first.\n"
    "2. State which math operation is needed at each step.\n"
    "3. Call the corresponding Python tool and wait for its result before moving to the next step."
)
