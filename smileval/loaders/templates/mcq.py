# overcomplicating formatting multiple choice questions
# but llms can be sensitive

ALPHABET = list("abcdefghijklmnopqrstuvwxyz")
CAPITAL_ALPHABET = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
FUNKY_ALPHABET =   list("WXYZABCDEFGHIJKLMNOPQRSTUV")
NUMBERS = list(range(1, 100))

SEP_DOT = "{}. {}"
SEP_ONE_SIDED = "{}) {}"
SEP_PARENTHESES = "({}) {}"
SEP_BRACKETS = "[{}] {}"

PRESENTATION_SELECTION_TYPES = {
    "alphabet": {
        "system": "Answer with only the letter of the correct answer given the question.",
        "choices": ALPHABET
    },
    "capital_alphabet": {
        "system": "Answer with only the letter of the correct answer given the question.",
        "choices": CAPITAL_ALPHABET
    },
     "funky_capital_alphabet": {
        "system": "Answer with only the letter of the correct answer given the question.",
        "choices": FUNKY_ALPHABET
    },
     "numbers": {
        "system": "Answer with only the number of the correct answer given the question.",
        "choices": NUMBERS
    }
}

def format_choices(answer_choices: list[str], symbols: list[str], sep: str, newline = "\n") -> str:
    choices_lines = []
    for pair in zip(answer_choices, symbols):
        choice, symbol = pair
        choices_lines.append(sep.format(symbol, choice))

    return newline.join(choices_lines)