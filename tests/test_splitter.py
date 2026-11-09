from src.scene_planner.splitter import (
    split_sentences,
    split_into_clauses,
    auto_group
)


# ---------------------------------
# 1. Tests for split_sentences()
# ---------------------------------

def test_normal_sentence_splitting():
    script = "Hello there. How are you? I am fine."

    result = split_sentences(script)

    assert result == [
        "Hello there.",
        "How are you?",
        "I am fine."
    ]


def test_abbreviation_handling():
    script = "Dr. Smith studies psychology. It is fascinating."

    result = split_sentences(script)

    assert len(result) == 2
    assert result[0] == "Dr. Smith studies psychology."


def test_decimal_handling():
    script = "The value is 3.5. That is interesting."

    result = split_sentences(script)

    assert len(result) == 2
    assert result[0] == "The value is 3.5."


def test_question_mark_handling():
    script = "Why do we overthink? Because we care."

    result = split_sentences(script)

    assert len(result) == 2


def test_quotation_handling():
    script = '"I made a mistake," she thought. Then she moved on.'

    result = split_sentences(script)

    assert len(result) == 2
    assert result[0] == '"I made a mistake," she thought.'


def test_ellipsis_handling():
    script = "Wait... what just happened?"

    result = split_sentences(script)

    assert len(result) == 1
    assert result[0] == script


def test_empty_script():
    assert split_sentences("") == []
    assert split_sentences("   ") == []


# ---------------------------------
# 2. Tests for split_into_clauses()
# ---------------------------------

def test_clause_splitting_creates_minimum_units():
    sentences = [
        "Your brain remembers awkward moments, and it keeps replaying them.",
        "You wonder why you said something so silly.",
        "This happens because your brain wants to understand what went wrong."
    ]

    result = split_into_clauses(sentences)

    assert len(result) >= 6


def test_clause_splitting_preserves_word_count():
    sentences = [
        "Your brain remembers awkward moments, and it keeps replaying them.",
        "You wonder why you said something so silly.",
        "This happens because your brain wants to understand what went wrong."
    ]

    result = split_into_clauses(sentences)

    original_words = sum(
        len(sentence.split()) for sentence in sentences
    )

    new_words = sum(
        len(clause.split()) for clause in result
    )

    assert original_words == new_words


def test_clause_splitting_preserves_exact_text():
    sentences = [
        "Your brain remembers awkward moments, and it keeps replaying them.",
        "You wonder why you said something so silly.",
        "This happens because your brain wants to understand what went wrong."
    ]

    result = split_into_clauses(sentences)

    reconstructed = " ".join(result)

    assert reconstructed == " ".join(sentences)


def test_clause_splitting_does_not_change_sufficient_units():
    sentences = [
        "Sentence one.",
        "Sentence two.",
        "Sentence three.",
        "Sentence four.",
        "Sentence five.",
        "Sentence six."
    ]

    result = split_into_clauses(sentences)

    assert result == sentences


# ---------------------------------
# 3. Tests for auto_group()
# ---------------------------------

def test_auto_group_creates_six_to_eight_scenes():
    sentences = [
        "Sentence number one.",
        "Sentence number two.",
        "Sentence number three.",
        "Sentence number four.",
        "Sentence number five.",
        "Sentence number six.",
        "Sentence number seven.",
        "Sentence number eight.",
        "Sentence number nine.",
        "Sentence number ten."
    ]

    result = auto_group(sentences)

    assert 6 <= len(result) <= 8


def test_auto_group_includes_every_sentence():
    sentences = [
        "Sentence number one.",
        "Sentence number two.",
        "Sentence number three.",
        "Sentence number four.",
        "Sentence number five.",
        "Sentence number six.",
        "Sentence number seven.",
        "Sentence number eight."
    ]

    result = auto_group(sentences)

    flattened = [
        number
        for group in result
        for number in group
    ]

    assert flattened == list(range(1, len(sentences) + 1))


def test_auto_group_preserves_sentence_order():
    sentences = [
        "First sentence.",
        "Second sentence.",
        "Third sentence.",
        "Fourth sentence.",
        "Fifth sentence.",
        "Sixth sentence.",
        "Seventh sentence."
    ]

    result = auto_group(sentences)

    flattened = [
        number
        for group in result
        for number in group
    ]

    assert flattened == sorted(flattened)


def test_auto_group_rejects_fewer_than_six_units():
    sentences = [
        "First sentence.",
        "Second sentence.",
        "Third sentence."
    ]

    try:
        auto_group(sentences)
        assert False, "Expected ValueError"
    except ValueError:
        pass