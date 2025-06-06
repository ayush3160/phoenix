import pytest
from strawberry.relay import GlobalID

from phoenix.db.models import SpanAnnotation
from phoenix.server.api.input_types.SpanAnnotationFilter import (
    SpanAnnotationFilter,
    SpanAnnotationFilterCondition,
    satisfies_filter,
)
from phoenix.server.api.types.AnnotationSource import AnnotationSource


@pytest.mark.parametrize(
    "span_annotation, filter, expected_satisfies",
    [
        pytest.param(
            SpanAnnotation(
                span_rowid=1,
                name="test-name",
                label="label",
                score=1.0,
                explanation="explanation",
                metadata_={},
                annotator_kind="HUMAN",
                source="API",
            ),
            SpanAnnotationFilter(include=SpanAnnotationFilterCondition(names=["test-name"])),
            True,
            id="matches-included-name",
        ),
        pytest.param(
            SpanAnnotation(
                span_rowid=1,
                name="span-annotation-name",
                label="label",
                score=1.0,
                explanation="explanation",
                metadata_={},
                annotator_kind="HUMAN",
                source="API",
            ),
            SpanAnnotationFilter(include=SpanAnnotationFilterCondition(names=["missing-name"])),
            False,
            id="does-not-match-included-name",
        ),
        pytest.param(
            SpanAnnotation(
                span_rowid=1,
                name="test-name",
                label="label",
                score=1.0,
                explanation="explanation",
                metadata_={},
                annotator_kind="HUMAN",
                source="API",
            ),
            SpanAnnotationFilter(exclude=SpanAnnotationFilterCondition(names=["test-name"])),
            False,
            id="matches-excluded-name",
        ),
        pytest.param(
            SpanAnnotation(
                span_rowid=1,
                name="test-name",
                label="label",
                score=1.0,
                explanation="explanation",
                metadata_={},
                annotator_kind="HUMAN",
                source="API",
            ),
            SpanAnnotationFilter(exclude=SpanAnnotationFilterCondition(names=["different-name"])),
            True,
            id="does-not-match-excluded-name",
        ),
        pytest.param(
            SpanAnnotation(
                span_rowid=1,
                name="test-name",
                label="label",
                score=1.0,
                explanation="explanation",
                metadata_={},
                annotator_kind="HUMAN",
                source="API",
            ),
            SpanAnnotationFilter(
                include=SpanAnnotationFilterCondition(sources=[AnnotationSource.API])
            ),
            True,
            id="matches-included-source",
        ),
        pytest.param(
            SpanAnnotation(
                span_rowid=1,
                name="test-name",
                label="label",
                score=1.0,
                explanation="explanation",
                metadata_={},
                annotator_kind="HUMAN",
                source="APP",
            ),
            SpanAnnotationFilter(
                include=SpanAnnotationFilterCondition(sources=[AnnotationSource.API])
            ),
            False,
            id="does-not-match-included-source",
        ),
        pytest.param(
            SpanAnnotation(
                span_rowid=1,
                name="test-name",
                label="label",
                score=1.0,
                explanation="explanation",
                metadata_={},
                annotator_kind="HUMAN",
                source="APP",
            ),
            SpanAnnotationFilter(
                exclude=SpanAnnotationFilterCondition(sources=[AnnotationSource.APP])
            ),
            False,
            id="matches-excluded-source",
        ),
        pytest.param(
            SpanAnnotation(
                span_rowid=1,
                name="test-name",
                label="label",
                score=1.0,
                explanation="explanation",
                metadata_={},
                annotator_kind="HUMAN",
                source="API",
            ),
            SpanAnnotationFilter(
                exclude=SpanAnnotationFilterCondition(sources=[AnnotationSource.APP])
            ),
            True,
            id="does-not-match-excluded-source",
        ),
        pytest.param(
            SpanAnnotation(
                span_rowid=1,
                name="test-name",
                label="label",
                score=1.0,
                explanation="explanation",
                metadata_={},
                annotator_kind="HUMAN",
                source="API",
                user_id=1,
            ),
            SpanAnnotationFilter(
                include=SpanAnnotationFilterCondition(user_ids=[GlobalID("User", "1")])
            ),
            True,
            id="matches-included-user-id",
        ),
        pytest.param(
            SpanAnnotation(
                span_rowid=1,
                name="test-name",
                label="label",
                score=1.0,
                explanation="explanation",
                metadata_={},
                annotator_kind="HUMAN",
                source="API",
                user_id=1,
            ),
            SpanAnnotationFilter(
                include=SpanAnnotationFilterCondition(user_ids=[GlobalID("User", "2")])
            ),
            False,
            id="does-not-match-included-user-id",
        ),
        pytest.param(
            SpanAnnotation(
                span_rowid=1,
                name="test-name",
                label="label",
                score=1.0,
                explanation="explanation",
                metadata_={},
                annotator_kind="HUMAN",
                source="API",
                user_id=None,
            ),
            SpanAnnotationFilter(
                include=SpanAnnotationFilterCondition(user_ids=[GlobalID("User", "1")])
            ),
            False,
            id="does-not-match-included-user-id-with-null-user-id",
        ),
        pytest.param(
            SpanAnnotation(
                span_rowid=1,
                name="test-name",
                label="label",
                score=1.0,
                explanation="explanation",
                metadata_={},
                annotator_kind="HUMAN",
                source="API",
                user_id=1,
            ),
            SpanAnnotationFilter(
                exclude=SpanAnnotationFilterCondition(user_ids=[GlobalID("User", "1")])
            ),
            False,
            id="matches-excluded-user-id",
        ),
        pytest.param(
            SpanAnnotation(
                span_rowid=1,
                name="test-name",
                label="label",
                score=1.0,
                explanation="explanation",
                metadata_={},
                annotator_kind="HUMAN",
                source="API",
                user_id=2,
            ),
            SpanAnnotationFilter(
                exclude=SpanAnnotationFilterCondition(user_ids=[GlobalID("User", "1")])
            ),
            True,
            id="does-not-match-excluded-user-id",
        ),
        pytest.param(
            SpanAnnotation(
                span_rowid=1,
                name="test-name",
                label="label",
                score=1.0,
                explanation="explanation",
                metadata_={},
                annotator_kind="HUMAN",
                source="API",
                user_id=None,
            ),
            SpanAnnotationFilter(
                exclude=SpanAnnotationFilterCondition(user_ids=[GlobalID("User", "1")])
            ),
            True,
            id="does-not-match-excluded-user-id-with-null-user-id",
        ),
        pytest.param(
            SpanAnnotation(
                span_rowid=1,
                name="test-name",
                label="label",
                score=1.0,
                explanation="explanation",
                metadata_={},
                annotator_kind="HUMAN",
                source="API",
                user_id=1,
            ),
            SpanAnnotationFilter(
                include=SpanAnnotationFilterCondition(
                    names=["test-name"],
                    sources=[AnnotationSource.API],
                    user_ids=[GlobalID("User", "1")],
                ),
                exclude=SpanAnnotationFilterCondition(
                    names=["other-name"],
                    sources=[AnnotationSource.APP],
                    user_ids=[GlobalID("User", "2")],
                ),
            ),
            True,
            id="matches-all-include-fields-and-no-exclude-fields",
        ),
        pytest.param(
            SpanAnnotation(
                span_rowid=1,
                name="test-name",
                label="label",
                score=1.0,
                explanation="explanation",
                metadata_={},
                annotator_kind="HUMAN",
                source="API",
                user_id=1,
            ),
            SpanAnnotationFilter(
                include=SpanAnnotationFilterCondition(
                    names=["test-name"],
                    sources=[AnnotationSource.API],
                    user_ids=[GlobalID("User", "1")],
                ),
                exclude=SpanAnnotationFilterCondition(names=["test-name"]),
            ),
            False,
            id="matches-all-include-fields-but-fails-on-exclude-name",
        ),
        pytest.param(
            SpanAnnotation(
                span_rowid=1,
                name="test-name",
                label="label",
                score=1.0,
                explanation="explanation",
                metadata_={},
                annotator_kind="HUMAN",
                source="API",
            ),
            SpanAnnotationFilter(
                include=SpanAnnotationFilterCondition(
                    names=["test-name", "other-name"],
                    sources=[AnnotationSource.API, AnnotationSource.APP],
                ),
            ),
            True,
            id="matches-multiple-included-names-and-sources",
        ),
        pytest.param(
            SpanAnnotation(
                span_rowid=1,
                name="test-name",
                label="label",
                score=1.0,
                explanation="explanation",
                metadata_={},
                annotator_kind="HUMAN",
                source="API",
            ),
            SpanAnnotationFilter(
                exclude=SpanAnnotationFilterCondition(
                    names=["test-name", "other-name"],
                    sources=[AnnotationSource.API, AnnotationSource.APP],
                ),
            ),
            False,
            id="matches-multiple-excluded-names-and-sources",
        ),
    ],
)
def test_satisfies_filter(
    span_annotation: SpanAnnotation,
    filter: SpanAnnotationFilter,
    expected_satisfies: bool,
) -> None:
    assert satisfies_filter(span_annotation, filter) == expected_satisfies
