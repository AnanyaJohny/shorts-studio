import re
from functools import lru_cache


def split_sentences(script: str) -> list[str]:
    """
    Split a script into sentences while preserving
    the original words and punctuation.
    """

    if not script or not script.strip():
        return []

    # Protect common abbreviations and decimal numbers.
    protected = script

    abbreviations = [
        "e.g.", "i.e.", "Mr.", "Mrs.", "Ms.",
        "Dr.", "Prof.", "etc."
    ]

    placeholders = {}

    for index, abbreviation in enumerate(abbreviations):
        placeholder = f"__ABBR{index}__"
        protected = protected.replace(abbreviation, placeholder)
        placeholders[placeholder] = abbreviation

    # Protect decimal numbers such as 3.5.
    protected = re.sub(
        r"(?<=\d)\.(?=\d)",
        "__DECIMAL__",
        protected
    )
    # Protect ellipses used as pauses before lowercase text.
    protected = re.sub(
    r"\.\.\.(?=\s+[a-z])",
    "__ELLIPSIS__",
    protected
)

    # Split at sentence-ending punctuation.
    # Keep closing quotation marks with their sentences.
    parts = re.split(
        r'(?<=[.!?])(?=["\')\]]?\s+)',
        protected
    )

    sentences = []

    for part in parts:
        part = part.strip()

        if not part:
            continue

        # Restore protected punctuation.
        for placeholder, abbreviation in placeholders.items():
            part = part.replace(placeholder, abbreviation)

        part = part.replace("__DECIMAL__", ".")
        part = part.replace("__ELLIPSIS__", "...")

        sentences.append(part)

    return sentences
def auto_group(

    sentences: list[str],

    target: int = 7

) -> list[list[int]]:

    """

    Group adjacent sentences into balanced scenes.

    Returns lists of 1-based sentence numbers.

    """

    if len(sentences) < 6:

        raise ValueError(

            "At least 6 sentence units are required. "

            "Long sentences must be split into clauses first."

        )

    # Keep the number of scenes between 6 and 8.

    target = max(6, min(8, target))

    group_count = min(len(sentences), target)

    # Calculate the word count of each sentence.

    word_counts = [

        len(sentence.split())

        for sentence in sentences

    ]

    total_words = sum(word_counts)

    ideal_words = total_words / group_count

    # Calculate cumulative word counts.

    prefix = [0]

    for count in word_counts:

        prefix.append(prefix[-1] + count)

    @lru_cache(maxsize=None)

    def find_best(start: int, groups_left: int):

        if groups_left == 0:

            if start == len(sentences):

                return 0, ()

            return float("inf"), ()

        best_cost = float("inf")

        best_groups = ()

        # Leave at least one sentence for every remaining group.

        max_end = len(sentences) - groups_left + 1

        for end in range(start + 1, max_end + 1):

            group_words = prefix[end] - prefix[start]

            cost = (group_words - ideal_words) ** 2

            remaining_cost, remaining_groups = find_best(

                end,

                groups_left - 1

            )

            total_cost = cost + remaining_cost

            if total_cost < best_cost:

                best_cost = total_cost

                best_groups = (

                    (start + 1, end),

                ) + remaining_groups

        return best_cost, best_groups

    _, ranges = find_best(0, group_count)

    # Convert ranges into lists of 1-based sentence numbers.

    return [

        list(range(start, end + 1))

        for start, end in ranges

    ]

def split_into_clauses(
    sentences: list[str],
    min_units: int = 6
) -> list[str]:
    """
    Split longer sentences into smaller clauses.
    Preserves original words and punctuation.
    """

    result = sentences.copy()

    conjunctions = (
        "and", "but", "because", "while",
        "although", "though", "so", "yet"
    )

    while len(result) < min_units:
        best_index = None
        best_split = None
        best_score = -1

        for index, sentence in enumerate(result):

            boundaries = []

            # Find comma boundaries.
            for match in re.finditer(r",\s*", sentence):
                boundaries.append(
                    (match.end(), match.end())
                )

            # Find conjunction boundaries.
            pattern = (
                r"\s+(" + "|".join(conjunctions) + r")\s+"
            )

            for match in re.finditer(
                pattern,
                sentence,
                flags=re.IGNORECASE
            ):
                boundaries.append(
                    (match.start(), match.start())
                )

            for start, end in boundaries:
                left = sentence[:start].strip()
                right = sentence[end:].strip()

                if len(left.split()) < 2:
                    continue

                if len(right.split()) < 2:
                    continue

                score = len(sentence.split())

                if score > best_score:
                    best_score = score
                    best_index = index
                    best_split = [left, right]

        if best_index is None:
            break

        result[best_index:best_index + 1] = best_split

    return result