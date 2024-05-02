from .base import Experiment, ExperimentMetadata, ExperimentContext, Loader

import random

class MCQQuestionAskExperiment(Experiment):
    def __init__(self, question: str, answer_choices: list[str], correct_answers: list[str] = []):
        self.question = question
        self.answer_choices = answer_choices
        self.correct_answers = correct_answers
        self.correct_indexes = [
            self.answer_choices.index(answer) for answer in correct_answers
        ]

    def execute(self, context: ExperimentContext) -> ExperimentOutcome:
        # TODO: raise warning when this is called cause you are supposed to overwrite
        return ExperimentOutcome(self.get_metadata(), context)