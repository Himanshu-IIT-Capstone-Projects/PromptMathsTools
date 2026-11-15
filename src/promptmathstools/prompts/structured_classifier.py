# prompts/04_structured_classifier.py
from typing import Literal
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

from promptmathstools.utility.loadllm import load_llm

class ProblemClassification(BaseModel):
    category: Literal["simple_arithmetic", "quadratic_equation", "word_problem"] = Field(
        description="Category of the math question."
    )
    suggested_tools: list[str] = Field(
        description="Names of tools likely needed (e.g., ['divide', 'multiply', 'subtract'])."
    )

def classify_problem(question: str) -> ProblemClassification:
    print("\n [classify_problem()] started")
    try:
        llm = load_llm()
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Classify the math question and list the tools needed to solve it."),
            ("human", "{question}"),
        ])
        chain = prompt | llm.with_structured_output(ProblemClassification)
        return chain.invoke({"question": question})
    except Exception as error:
        print(f"\n [classify_problem()] error: {error!r}")
        raise
    finally:
        print("\n [classify_problem()] ended")
