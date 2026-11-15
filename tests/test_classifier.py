from promptmathstools.prompts.structured_classifier import classify_problem

# Test cases for the classify_problem function
def test_classifier_categories():
    res1 = classify_problem("What is 3 + 2?")
    assert res1.category == "simple_arithmetic"

    res2 = classify_problem("Find x for (x + 2)(x - 3) = 0")
    assert res2.category == "quadratic_equation"

    res3 = classify_problem("I have 100 rupees, bought 500gm apples. 10kg costs 1000 rupees, balance?")
    assert res3.category == "word_problem"
