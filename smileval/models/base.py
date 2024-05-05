# THis file should not load any dependencies in specific
import asyncio
import os

class ChatMessage:
    def __init__(self, content: str, role: str = "user"):
        self.content = content
        self.role = role
        self.is_generated = False

    def mark_as_generated(self):
        self.is_generated = True
        return self # allow chaining

    def as_dict(self):
        return {
            "content": self.content,
            "role": self.role
        }

    def __repr__(self):
        return "<{}: {}>".format(self.role, self.content)

    def __str__(self):
        return "<{}: {}>".format(self.role, self.content)
    
    # a bit unpythonic but there if I need it
    def clone(self):
        return ChatMessage(self.content, self.role)

    # why do these exist? I forgot.
    def is_system(self):
        return self.role == "system"

    def is_user(self):
        return self.role == "user"

    def is_assistant(self):
        return self.role == "assistant"

    def unsystem_prompt(self):
        '''
        Some models like certain Llama models may not allow a system prompt. This is a bad hack to fake a system prompt as a user message but it is recommended to use the utility message to rewrite a message chain. This should be opt in as I highly suspect it may affect evaluations.
        '''
        assert self.role == "system", ValueError("Chat message is not of system role.")
        self.content = f"# System\n{self.content}"

    # you can't depend on yourself directly without a string
    @staticmethod
    def to_api_format(messages: "list[ChatMessage]"):
        return [
            chat_message.as_dict() for chat_message in messages
        ]

    @staticmethod
    def from_dict(message):
        return ChatMessage(message["content"], message["role"] if message["role"] else "user")

# TODO: add tests
# TODO: We can make async methods sync by running them with asyncio, but prioritze async stuff first because we can run requests in parellel if a model has an efficient batching endpoint setup to get a massive performance boost.
def unsystem_prompt_chain(messages: list[ChatMessage]):
    '''
    Models like Mixtral don't have a system prompt but a friend made up this hack by prepending the system message 2 line breaks before the first user message that works suprisingly well.
    '''
    system_messages_merge = ""
    # why would you use more than one system message
    for system_message in filter(lambda m: m.role == "system", messages):
        system_messages_merge += system_messages_merge + system_message.content + "\n"
    other_messages = list(filter(lambda m: m.role != "system", messages))
    assert len(other_messages) > 0, "Cannot unsystem message a message chain with only system messages."
    assert other_messages[0].is_user(), "First non-system message must be from user"
    other_messages[0] =  other_messages[0].clone()
    other_messages[0].content = system_messages_merge + "\n" + other_messages[0].content
    return other_messages

def minimize(inp):
    out = inp.copy()
    dels = []
    for key in out:
        if out[key] is None:
            dels.append(key)

    for key in dels:
        del out[key]
    return out

class ChatCompletionOptions:
    def __init__(self, seed: int | None = None, **kwargs):
        # use defaults
        self.temperature: float | None = None
        self.top_p: float | None = None
        self.top_k: int | None = None
        self.instruction_template: str | None = None
        self.seed: int | None = seed
        self.use_system_prompt_workaround = None
        self.stop_tokens = None
        self.max_tokens: int | None = None
        # bad hack ig
        self.__dict__.update(kwargs)

    def update(self, new_dict):
        self.__dict__.update(new_dict)

    @staticmethod
    def merge(a: "ChatCompletionOptions", b: "ChatCompletionOptions"):
        merged = {
            **minimize(a.as_dict()),
            **minimize(b.as_dict())
        }
        return ChatCompletionOptions(**merged)

    def as_dict(self):
        return vars(self)

default_options = ChatCompletionOptions()

class ChatCompletionModel:
    def __init__(self, name: str):
        self.name = name



    # apparently in python coroutine return type is implied unlike js typings
    # TODO: what if you have multiple completions? prob low priority

    def preprocess_inputs(self, messages: list[ChatMessage], options: ChatCompletionOptions) -> [list[ChatMessage], ChatCompletionOptions]:
        if options.use_system_prompt_workaround:
            messages = unsystem_prompt_chain(messages[:])
        return messages, options

    async def chat_complete(self, messages: list[ChatMessage], options: ChatCompletionOptions) ->  ChatMessage:
        raise NotImplementedError("chat_complete needs to be implemented for " + str(self))

    def chat_complete_log_request(self, messages: list[ChatMessage], options: ChatCompletionOptions) ->  ChatMessage:
        if os.getenv("SMILEVAL_LOG_COMPLETIONS"):
            print(messages)

    def chat_complete_log_response(self, response: str) ->  ChatMessage:
        if os.getenv("SMILEVAL_LOG_COMPLETIONS"):
            print("Returned back ",response)
class EmbeddingModel:
    def __init__(self, name: str):
        self.name = name

    def normalize_args(self, messages: str | list[str]) -> list[str]:
        if type(messages) == str:
            return [messages]

    # numpy array support?
    async def embed(self, messages: str | list[str]) -> list[list[float]]:
        raise NotImplementedError("embed needs to be implemented for " + str(self))