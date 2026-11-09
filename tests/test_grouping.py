from src.scene_planner.models import SceneGroup, SceneGrouping
from src.scene_tester.validator import validate_grouping
from src.scene_planner.planner import build_scene_plan

def make_grouping(sentence_groups):
    """Create a SceneGrouping for testing."""

    return SceneGrouping(
        scenes=[
            SceneGroup(
                sentences=numbers,
                visual_description="A stickman thinking."
            )
            for numbers in sentence_groups
        ]
    )


def test_valid_grouping_passes():
    grouping = make_grouping([
        [1, 2],
        [3],
        [4],
        [5],
        [6],
        [7, 8]
    ])

    issues = validate_grouping(grouping, 8)

    assert issues == []


def test_missing_sentence_is_detected():
    grouping = make_grouping([
        [1], [2], [3], [4], [5], [6]
    ])

    issues = validate_grouping(grouping, 8)

    assert any("missing" in issue.lower() for issue in issues)


def test_duplicate_sentence_is_detected():
    grouping = make_grouping([
        [1], [2], [3], [4], [5], [5, 6]
    ])

    issues = validate_grouping(grouping, 6)

    assert any("duplicate" in issue.lower() for issue in issues)


def test_invalid_sentence_number_is_detected():
    grouping = make_grouping([
        [1], [2], [3], [4], [5], [7]
    ])

    issues = validate_grouping(grouping, 6)

    assert any("invalid" in issue.lower() for issue in issues)


def test_out_of_order_sentences_are_detected():
    grouping = make_grouping([
        [2, 1], [3], [4], [5], [6], [7]
    ])

    issues = validate_grouping(grouping, 7)

    assert any("ascending order" in issue.lower() for issue in issues)


def test_non_contiguous_sentences_are_detected():
    grouping = make_grouping([
        [1, 3], [2], [4], [5], [6], [7]
    ])

    issues = validate_grouping(grouping, 7)

    assert any("non-contiguous" in issue.lower() for issue in issues)


def test_scene_order_is_checked():
    grouping = make_grouping([
        [2], [1], [3], [4], [5], [6]
    ])

    issues = validate_grouping(grouping, 6)

    assert any("correct order" in issue.lower() for issue in issues)


def test_empty_visual_description_is_detected():
    grouping = SceneGrouping(
        scenes=[
            SceneGroup(
                sentences=[i],
                visual_description=""
            )
            for i in range(1, 7)
        ]
    )

    issues = validate_grouping(grouping, 6)

    assert any("empty visual description" in issue.lower() for issue in issues)


def test_too_few_scenes_are_detected():
    grouping = make_grouping([
        [1], [2], [3], [4], [5]
    ])

    issues = validate_grouping(grouping, 5)

    assert any("expected 6-8 scenes" in issue.lower() for issue in issues)


def test_build_scene_plan_preserves_original_narration():

    sentences = [
        "Your brain remembers awkward moments.",
        "It keeps replaying them.",
        "You wonder why you said something silly.",
        "This happens because your brain wants answers.",
        "It tries to understand what went wrong.",
        "But replaying the moment won't change it."
    ]

    grouping = SceneGrouping(
        scenes=[
            SceneGroup(
                sentences=[1],
                visual_description="A stickman thinking."
            ),
            SceneGroup(
                sentences=[2],
                visual_description="A stickman replaying a memory."
            ),
            SceneGroup(
                sentences=[3],
                visual_description="A stickman looking embarrassed."
            ),
            SceneGroup(
                sentences=[4],
                visual_description="A stickman examining a thought."
            ),
            SceneGroup(
                sentences=[5],
                visual_description="A stickman looking confused."
            ),
            SceneGroup(
                sentences=[6],
                visual_description="A stickman moving forward."
            )
        ]
    )

    scene_plan = build_scene_plan(sentences, grouping)

    reconstructed = " ".join(
        scene.narration for scene in scene_plan.scenes
    )

    original = " ".join(sentences)

    assert reconstructed == original
    assert len(scene_plan.scenes) == 6
    assert [
        scene.scene_number for scene in scene_plan.scenes
    ] == [1, 2, 3, 4, 5, 6]