"""Validation helpers for the council briefing JSON consumed by downstream sites."""

from __future__ import annotations

import re
from typing import Any


QUESTION_ID_PATTERN = re.compile(r"q[1-9][0-9]*$")
ANSWER_KEYS = {"answer_1", "answer_2", "answer_3"}
PUBLISHED_ANSWER_KEYS = ANSWER_KEYS | {"answer_4"}


class CouncilValidationError(ValueError):
    """Raised when a council briefing does not satisfy the V2 contract."""


def _require_string(value: Any, path: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise CouncilValidationError(f"{path} must be a non-empty string")


def is_legacy_briefing(data: Any) -> bool:
    """Return whether data uses the pre-V2 key_points format."""
    if not isinstance(data, dict) or not isinstance(data.get("key_points"), list):
        return False
    points = data["key_points"]
    return bool(points) and isinstance(points[0], dict) and "theme" in points[0]


def validate_consumer_contract(data: Any) -> None:
    """Validate fields dereferenced by the Astro council page renderer.

    Historical files span multiple schemas, so this compatibility check ignores
    legacy points and error placeholders while strictly checking every V2
    deliberation item that a consumer will render.
    """
    if not isinstance(data, dict) or not isinstance(data.get("key_points"), list):
        raise CouncilValidationError("briefing.key_points must be an array")
    for point_index, point in enumerate(data["key_points"]):
        if not isinstance(point, dict):
            raise CouncilValidationError(f"key_points[{point_index}] must be an object")
        if "deliberation_items" not in point:
            continue
        items = point["deliberation_items"]
        if not isinstance(items, list):
            raise CouncilValidationError(
                f"key_points[{point_index}].deliberation_items must be an array"
            )
        for item_index, item in enumerate(items):
            path = f"key_points[{point_index}].deliberation_items[{item_index}]"
            if not isinstance(item, dict):
                raise CouncilValidationError(f"{path} must be an object")
            _require_string(item.get("question_id"), f"{path}.question_id")


def validate_council_briefing(
    data: Any,
    *,
    expected_date: str | None = None,
    generated: bool = False,
) -> None:
    """Validate the V2 briefing structure.

    ``generated=True`` validates the raw model response, which must contain exactly
    three answer choices. Published briefings may additionally contain the
    programmatically-added ``answer_4`` fallback.
    """
    if not isinstance(data, dict):
        raise CouncilValidationError("briefing must be a JSON object")

    for field in ("date", "meeting_context", "monthly_goal", "daily_focus"):
        _require_string(data.get(field), field)
    if expected_date is not None and data["date"] != expected_date:
        raise CouncilValidationError(
            f"date must match output date {expected_date!r}, got {data['date']!r}"
        )

    points = data.get("key_points")
    if not isinstance(points, list) or not points:
        raise CouncilValidationError("key_points must be a non-empty array")

    seen_question_ids: set[str] = set()
    for point_index, point in enumerate(points):
        point_path = f"key_points[{point_index}]"
        if not isinstance(point, dict):
            raise CouncilValidationError(f"{point_path} must be an object")
        _require_string(point.get("topic"), f"{point_path}.topic")
        _require_string(point.get("summary"), f"{point_path}.summary")

        items = point.get("deliberation_items")
        if not isinstance(items, list) or not items:
            raise CouncilValidationError(
                f"{point_path}.deliberation_items must be a non-empty array"
            )

        for item_index, item in enumerate(items):
            item_path = f"{point_path}.deliberation_items[{item_index}]"
            if not isinstance(item, dict):
                raise CouncilValidationError(f"{item_path} must be an object")

            question_id = item.get("question_id")
            _require_string(question_id, f"{item_path}.question_id")
            if not QUESTION_ID_PATTERN.fullmatch(question_id):
                raise CouncilValidationError(
                    f"{item_path}.question_id must match q1, q2, ..."
                )
            if generated and question_id in seen_question_ids:
                raise CouncilValidationError(f"duplicate question_id {question_id!r}")
            seen_question_ids.add(question_id)
            _require_string(item.get("text"), f"{item_path}.text")

            context = item.get("context")
            if context is not None:
                if not isinstance(context, list):
                    raise CouncilValidationError(f"{item_path}.context must be an array")
                for context_index, context_item in enumerate(context):
                    _require_string(
                        context_item, f"{item_path}.context[{context_index}]"
                    )

            answers = item.get("multiple_choice_answers")
            if not isinstance(answers, dict):
                raise CouncilValidationError(
                    f"{item_path}.multiple_choice_answers must be an object"
                )
            expected_keys = ANSWER_KEYS if generated else PUBLISHED_ANSWER_KEYS
            if generated:
                keys_are_valid = set(answers) == expected_keys
            else:
                keys_are_valid = set(answers) in (ANSWER_KEYS, PUBLISHED_ANSWER_KEYS)
            if not keys_are_valid:
                raise CouncilValidationError(
                    f"{item_path}.multiple_choice_answers has invalid keys: "
                    f"{sorted(answers)}"
                )

            for answer_key, answer in answers.items():
                answer_path = f"{item_path}.multiple_choice_answers.{answer_key}"
                if not isinstance(answer, dict):
                    raise CouncilValidationError(f"{answer_path} must be an object")
                _require_string(answer.get("text"), f"{answer_path}.text")
                implication = answer.get("implication")
                if implication is not None:
                    _require_string(implication, f"{answer_path}.implication")
