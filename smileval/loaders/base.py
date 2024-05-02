
from ..models import ChatCompletionModel, ChatCompletionOptions, EmbeddingModel, ChatMessage

class ExperimentContext:
    def __init__(self, chat_model: ChatCompletionModel):
        self.chat_model: ChatCompletionModel = chat_model
        self.embedding_model: EmbeddingModel | None = None
        self.chat_model_options: ChatCompletionOptions | None = None
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

    async def generate(self, message: str) -> str:
        chain = []
        if self.default_system_prompt is not None:
            chain.append(ChatMessage(content = self.default_system_prompt, role = "system"))
        chain.append(ChatMessage(message))
        return (await self.chat_model.chat_complete(chain, self.chat_model_options))["content"]

class ExperimentMetadata:
    def __init__(self, name: str | None = None, weight: int = 1):
        if name:
            self.name: str | None = name
        else:
            self.name: str | None = None

        self.weight: int = weight
        self.tags = []

    def add_tag(self, tag: str):
        self.tags.append(tag)
        return self

# the end goal is to be able to have a generated html webpage by tag


class Experiment:
    def execute(self, context: ExperimentContext):
        pass

# generator of experiments
class Loader:
    pass