from ..judge import *


def test_judge_answer_when_exact_match():
    assert judge_answer("mitochondria", "mitochondria") is True


def test_judge_answer_when_not_exact_match():
    assert judge_answer("mitochondria", "golgi body") is False


def test_judge_answer_when_no_answer():
    assert judge_answer("", "mitochondria") is False


def test_judge_answer_when_fuzzy_match():
    assert judge_answer("mitocondrjis", "mitochondria") is True


def test_judge_answer_when_single_bracket_match():
    assert (
        judge_answer(
            "mitochondria", "Accept {mitochondria} [do not accept golgi body]"
        )
        is True
    )
    assert (
        judge_answer(
            "golgi body", "Accept {mitochondria} [do not accept golgi body]"
        )
        is False
    )


def test_judge_answer_when_multi_bracket_match():
    assert (
        judge_answer(
            "mitochondria",
            "Accept {mitochondria} or {the powerhouse of the cell}",
        )
        is True
    )
    assert (
        judge_answer(
            "powerhouse of the cell",
            "Accept {mitochondria} or {the powerhouse of the cell}",
        )
        is True
    )


def test_judge_answer_when_more_parts_in_user_answer():
    assert (
        judge_answer(
            "Krebs cycle",
            "{Krebs} cycle [accept {citric acid cycle} before mentioned]",
        )
        is True
    )
    assert (
        judge_answer(
            "atilla the hun",
            "Atilla",
        )
        is True
    )
    assert (
        judge_answer(
            "atilla the hun, the golden horde, and victor hugo maybe",
            "Atilla",
        )
        is False
    )


def test_judge_answer_when_fewer_parts_in_user_answer():
    assert (
        judge_answer(
            "Krebs",
            "Krebs cycle",
        )
        is True
    )
    assert (
        judge_answer(
            "atilla",
            "Atilla the Hun",
        )
        is True
    )
    assert (
        judge_answer(
            "a",
            "Atilla",
        )
        is False
    )
