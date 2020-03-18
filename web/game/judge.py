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
    
    return compare_answers(user_answer, major_answers) >= 80


def compare_answers(user_answer, major_answers):
    """Compares user answer words with major answer words
    """
    # TODO: Make it so sequences matter

    user_words = user_answer.split(" ")
    ratios = []

    for major_answer in major_answers:
        n = 0
        r = 0
        for user_word in user_words:
            for major_word in major_answer.split(" "):
                r = max(fuzz.ratio(user_word, major_word), r)
        ratios.append(r)

    return max(ratios)