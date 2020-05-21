import re
from fuzzywuzzy import fuzz

major_matcher = re.compile(r'(?<={).*?(?=})')

def judge_answer(user_answer, question_answer):
    """Judge answer response as correct or not
    """

    user_answer = user_answer.lower()
    question_answer = question_answer.lower()

    if user_answer == "":
        return False

    major_answers = major_matcher.findall(question_answer)
    if len(major_answers) <= 0:
        major_answers = [question_answer]
    
    r = 0.8*compare_answer_tokens(user_answer, major_answers) + \
        0.2*compare_answer_partial(user_answer, major_answers)

    return r >= 0.7


def compare_answer_tokens(user_answer, major_answers):
    """Compare by ordered tokens"""
    return max(fuzz.token_sort_ratio(user_answer, major_answer)/100 for major_answer in major_answers)

def compare_answer_partial(user_answer, major_answers):
    """Compare by partial"""
    return max(fuzz.partial_ratio(user_answer, major_answer)/100 for major_answer in major_answers)