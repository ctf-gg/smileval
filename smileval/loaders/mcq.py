from .base import Experiment, ExperimentMetadata, ExperimentContext, ExperimentOutcome, Loader

from ..models import ChatMessage

import random
import csv
import json

from .templates import mcq as mcq_templates
from ..utils import sha256

default_formatting = {
    "presentation_selection_type": mcq_templates.PRESENTATION_SELECTION_TYPES["capital_alphabet"],
    "question_answer_format": "{}\n{}",
    "sep": mcq_templates.SEP_BRACKETS
}

MCQ_EXAMPLE_QUESTION = "What color is the sky?"
MCQ_EXAMPLE_ANSWERS = ["Pink", "Blue", "Violet", "Red"]
MCQ_EXAMPLE_CORRECT_INDEX = 1

class MCQQuestionAskExperiment(Experiment):
    def __init__(self, question: str, answer_choices: list[str], correct_answers: list[str] = [], formatting = default_formatting, points: int = 1, use_shuffle = False, use_example = False, use_strict = False):
        self.question = question
        self.answer_choices = answer_choices
        self.correct_answers = correct_answers
        # prob won't use this in case of shuffling
        # print(self.correct_answers, answer_choices)
        self.correct_indexes = [
            self.answer_choices.index(answer) for answer in correct_answers
        ]
        self.metadata = ExperimentMetadata(self.gen_id(), points)
        # give one sample interaction chain to help weaker LLMs
        self.use_example = use_example
        self.shuffle = use_shuffle
        self.max_points = points
        self.formatting = formatting
        self.use_strict = use_strict

    def gen_id(self):
        # question is not shuffled yet so we can id it
        self.backup_answer_choices = self.answer_choices[:]
        self.answer_choices = sorted(self.answer_choices)
        text = self.format_question(default_formatting)
        q_id = sha256(text)[:6]
        self.answer_choices = self.backup_answer_choices
        return q_id

    def format_question_example(self, formatting_override = None) -> str:
        qa_format = formatting_override if formatting_override else self.formatting
        return qa_format["question_answer_format"].format(MCQ_EXAMPLE_QUESTION,mcq_templates.format_choices(MCQ_EXAMPLE_ANSWERS, qa_format["presentation_selection_type"]["choices"], qa_format["sep"]))

    def format_question(self, formatting_override = None) -> str:
        qa_format = formatting_override if formatting_override else self.formatting
        return qa_format["question_answer_format"].format(self.question,mcq_templates.format_choices(self.answer_choices, qa_format["presentation_selection_type"]["choices"], qa_format["sep"]))

    async def execute(self, context: ExperimentContext) -> ExperimentOutcome:
        outcome = ExperimentOutcome(self.get_metadata(), context)

        answer_choices = self.answer_choices[:]

        if self.shuffle:
            random.shuffle(answer_choices)

        prompt = self.format_question()

        system_prompt = default_formatting["presentation_selection_type"]["system"]

        shot_messages = []

        if self.use_example:
            shot_messages.extend([
                ChatMessage(content = self.format_question_example(), role = "user"),
                ChatMessage(self.formatting["presentation_selection_type"]["choices"][MCQ_EXAMPLE_CORRECT_INDEX], role = "assistant")
            ])

        answer = await context.generate(prompt, system_prompt, shot_messages = shot_messages)

        symbols = self.formatting["presentation_selection_type"]["choices"]

        if answer in symbols:
            chosen_index = symbols.index(answer)
            if chosen_index < len(answer_choices):
                answer_text = answer_choices[chosen_index]
                if answer_text in self.correct_answers:
                    outcome.set_score_off_bool(True)
        # print("Strict",self.use_strict)
        if not self.use_strict:
            # reverse
            correct_symbols = [self.formatting["sep"].format(self.formatting["presentation_selection_type"]["choices"][answer_choices.index(correct_answer)], "").strip() for correct_answer in self.correct_answers]
            # print("Correct symbols",correct_symbols)
            for correct_symbol in correct_symbols:
                if correct_symbol in answer:
                    outcome.set_score_off_bool(True)
        print("Outcome", outcome.score, " score")
        return outcome

    def get_metadata(self) -> ExperimentMetadata:
        return self.metadata

class MCQQuestionLoader(Loader):
    def __init__(self, input_file_path: str, formatting_config: dict = default_formatting, mode: str | None = None, skip_first_item = False, use_shuffle = False, use_example = False, use_strict = False):
        self.input_file_path = input_file_path
        self.input_file = open(input_file_path, "r")
        self.formatting_config = formatting_config
        self.mode = mode
        if self.mode == None:
            if self.input_file_path.endswith(".csv"):
                self.mode = "csv"
                self.proxy_reader = csv.reader(self.input_file)
                if skip_first_item:
                    _ = next(self.proxy_reader)
        self.use_shuffle = use_shuffle
        self.use_example = use_example
        self.use_strict = use_strict

    def __next__(self) -> Experiment:
        try:
            if self.mode == "csv":
                line = next(self.proxy_reader)
                answer = line.pop()
                question = line.pop(0)
                answer_choices = line[:]
                return MCQQuestionAskExperiment(question, answer_choices, correct_answers = [answer], formatting = self.formatting_config, use_shuffle = self.use_shuffle, use_example = self.use_example, use_strict = self.use_strict)
        except StopIteration:
            self.input_file.close()
            raise StopIteration()