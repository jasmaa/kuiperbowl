from fuzzywuzzy import fuzz

def judge_answer(user_answer, question_answer):
    """Judge answer response as correct or not
    """

    ratio = fuzz.partial_ratio(user_answer, question_answer)

    return user_answer != "" and ratio >= 60