
class ChatMessage:
    def __init__(self, content: str, role: str = "user"):
        self.content = content
        self.role = role

    def as_dict(self):
        return {
            "content": content,
            "role": role
        }
    
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
        Some models like certain Llama models may not allow a system prompt. This is a bad hack to fake a system prompt as a user message but it is recommended to use the utility message to rewrite a message chain.
        '''
        assert self.role == "system"
        self.content = f"# System\n{self.content}"
    @staticmethod
    def from_dict(message):
        return ChatMessage(message["content"], message["role"] if message["role"] else "user")

# TODO: add tests
def unsystem_prompt_chain(messages: list[ChatMessage]):
    '''
    Models like Mixtral don't have a system prompt but a friend made up this hack by prepending the system message 2 line breaks before the first user message that works suprisingly well.
    '''
    system_messages_merge = ""
    # why would you use more than one system message
    for system_message in filter(lambda m: m.role == "system", messages):
        system_messages_merge += system_message_merge + system_message.content + "\n"
    other_messages = list(filter(lambda m: m.role != "system", messages))
    assert len(other_messages) > 0, "Cannot unsystem message a message chain with only system messages."
    assert other_messages[0].is_user(), "First non-system message must be from user"
    other_messages[0].content = system_messages_merge + "\n" + other_messages[0].content
    return other_messages

class ChatCompletionOptions:
    def __init__(self):
        # use defaults
        self.temperature: float | None = None
        self.top_p: float | None = None
        self.top_k: int | None = None
        self.instruction_template: str | None = None
        self.seed: int | None = None

    def as_dict(self):
        return vars(self)

default_options = ChatCompletionOptions()

class ChatCompletionModel:
    def __init__(self, name: str):
        self.name = name

    def chat_complete(messages: list[ChatMessage], options: ChatCompletionOptions = default_options) ->  ChatMessage:
        raise NotImplementedError("chat_complete needs to be implemented for " + str(self))
class EmbeddingModel:
    def __init__(self, name: str):
        self.name = name

    def normalize_args(messages: str | list[str]) -> list[str]:
        if type(messages) == str:
            return [messages]

    # numpy array support?
    def embed(messages: str | list[str]) -> list[list[float]]:
        raise NotImplementedError("embed needs to be implemented for " + str(self))