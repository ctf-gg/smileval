
from ..models import ChatCompletionModel, ChatCompletionOptions, EmbeddingModel, ChatMessage

class ExperimentContext:
    def __init__(self, chat_model: ChatCompletionModel):
        self.chat_model: ChatCompletionModel = chat_model
        self.embedding_model: EmbeddingModel | None = None
        self.chat_model_options: ChatCompletionOptions | None = ChatCompletionOptions()
        self.seed: int | None = None
        self.default_system_prompt: str | None = None 

    def use_embedding_model(self, embedding_model: EmbeddingModel):
        self.embedding_model = embedding_model
        return self # for chaining

    def set_seed(self, seed: int):
        self.seed = seed
        return self

    def use_system_prompt(self, prompt: str):
        self.default_system_prompt = prompt
        return self

    def model_id(self) -> str:
        return str(type(self.chat_model)) + ":" + self.chat_model.name

    def summary(self):
        summary_dict = {
            "model": self.model_id,
        }
        if self.seed:
            summary_dict["seed"] = seed
        return summary_dict

    async def generate(self, message: str, system_prompt: str | None = None, shot_messages: list[ChatMessage] | None = None) -> str:
        chain = []
        if self.default_system_prompt is not None and not system_prompt:
            chain.append(ChatMessage(content = self.default_system_prompt, role = "system"))
        elif system_prompt is not None:
            chain.append(ChatMessage(content = system_prompt, role = "system"))
        if shot_messages:
            chain.extend(shot_messages)
        chain.append(ChatMessage(message))
        final_options = ChatCompletionOptions.merge(self.chat_model_options, ChatCompletionOptions(seed = self.seed)) if self.chat_model_options else ChatCompletionOptions(seed = self.seed)
        return (await self.chat_model.chat_complete(chain, final_options)).content

class ExperimentMetadata:
    def __init__(self, name: str | None = None, weight: int = 1):
        if name:
            self.name: str | None = name
        else:
            self.name: str | None = None

        self.weight: int = weight
        self.tags = ["default"]

    def add_tag(self, tag: str):
        self.tags.append(tag)
        return self

    def has_tag(self, tag: str) -> bool:
        return tag in self.tags
# the end goal is to be able to have a generated html webpage by tag

class ExperimentOutcome:
    def __init__(self, experiment_meta: ExperimentMetadata, context: ExperimentContext):
        self.exp_meta: ExperimentMetadata = experiment_meta
        self.score = 0
        self.context: ExperimentContext = context

    def set_score(self, new_score: int):
        self.score = new_score
        return self

    def serialize(self):
        return {
            "score": self.score,
            "weight": self.exp_meta.weight,
            "tags": self.exp_meta.tags,
            "name": self.exp_meta.name
        }

    def set_score_off_bool(self, status: bool):
        self.score = self.exp_meta.weight if status else 0
        return self

class Experiment:
    async def execute(self, context: ExperimentContext) -> ExperimentOutcome:
        # TODO: raise warning when this is called cause you are supposed to overwrite
        return ExperimentOutcome(self.get_metadata(), context)

    def get_metadata(self) -> ExperimentMetadata:
        raise NotImplemented()

# generator of experiments
class Loader:
    # async variant in the future?
    def __next__(self) -> Experiment:
        raise StopIteration()

    # autoresume can be implemented using this
    def is_determinisitic(self) -> bool:
        return False

    # return -1 if unknown
    def num_experiments(self) -> int:
        return 0

    def __iter__(self):
        return self