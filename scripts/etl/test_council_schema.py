#!/usr/bin/env python3

import copy
import unittest

from council_schema import (
    CouncilValidationError,
    validate_consumer_contract,
    validate_council_briefing,
)


def valid_briefing():
    return {
        "date": "2026-06-16",
        "meeting_context": "context",
        "monthly_goal": "goal",
        "daily_focus": "focus",
        "key_points": [
            {
                "topic": "topic",
                "summary": "summary",
                "deliberation_items": [
                    {
                        "question_id": "q1",
                        "text": "question",
                        "context": ["evidence"],
                        "multiple_choice_answers": {
                            f"answer_{number}": {"text": f"choice {number}"}
                            for number in range(1, 4)
                        },
                    }
                ],
            }
        ],
    }


class CouncilSchemaTests(unittest.TestCase):
    def test_accepts_valid_generated_briefing(self):
        validate_council_briefing(
            valid_briefing(), expected_date="2026-06-16", generated=True
        )

    def test_rejects_topic_nested_as_deliberation_item(self):
        data = valid_briefing()
        data["key_points"][0]["deliberation_items"].append(
            {"topic": "nested topic", "summary": "wrong level"}
        )

        with self.assertRaisesRegex(CouncilValidationError, "question_id"):
            validate_council_briefing(data, generated=True)
        with self.assertRaisesRegex(CouncilValidationError, "question_id"):
            validate_consumer_contract(data)

    def test_rejects_duplicate_question_ids(self):
        data = valid_briefing()
        duplicate = copy.deepcopy(data["key_points"][0]["deliberation_items"][0])
        data["key_points"][0]["deliberation_items"].append(duplicate)

        with self.assertRaisesRegex(CouncilValidationError, "duplicate question_id"):
            validate_council_briefing(data, generated=True)

    def test_published_briefing_allows_other_answer(self):
        data = valid_briefing()
        data["key_points"][0]["deliberation_items"][0][
            "multiple_choice_answers"
        ]["answer_4"] = {"text": "Other", "implication": None}

        validate_council_briefing(data)


if __name__ == "__main__":
    unittest.main()
