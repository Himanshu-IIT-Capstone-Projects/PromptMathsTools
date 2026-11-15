from langchain_core.prompts import ChatPromptTemplate
from promptmathstools.prompts.structured_classifier import ProblemClassification
from promptmathstools.utility.loadllm import load_llm

# Helper to run classifier asynchronously without blocking FastAPI's event loop
async def classify_problem_async(question: str):
    print("\n [classify_problem_async()] started")
    try:
        llm = load_llm()
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Classify the math question and list the tools needed to solve it."),
            ("human", "{question}"),
        ])
        chain = prompt | llm.with_structured_output(ProblemClassification)
        return await chain.ainvoke({"question": question})
    except Exception as error:
        print(f"\n [classify_problem_async()] error: {error!r}")
        raise
    finally:
        print("\n [classify_problem_async()] ended")