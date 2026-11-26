"""The frozen question sets: what every system is asked, in the same words.

Each question is a yes/no predicate. Decision models answer with a probability
of "yes"; rules and LLMs answer true or false. The four reported decision
outputs are derived from these answers by `triallab.reference.derive`.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from triallab.config import CONFIGS

QUESTIONS_PATH = CONFIGS / "questions-v1.json"


@dataclass(frozen=True)
class Question:
    id: str
    text: str
    criteria_true: str
    criteria_false: str


@dataclass(frozen=True)
class QuestionSet:
    version: str
    name: str
    context: str
    questions: tuple[Question, ...]

    @property
    def ids(self) -> tuple[str, ...]:
        return tuple(q.id for q in self.questions)


def load_question_set(name: str, path: Path = QUESTIONS_PATH) -> QuestionSet:
    raw = json.loads(path.read_text())
    if name not in raw["sets"]:
        raise ValueError(f"unknown question set {name!r}; choose from {', '.join(raw['sets'])}")
    entry = raw["sets"][name]
    return QuestionSet(
        version=raw["version"],
        name=name,
        context=entry["context"],
        questions=tuple(
            Question(id=q["id"], text=q["text"], criteria_true=q["true"], criteria_false=q["false"])
            for q in entry["questions"]
        ),
    )
