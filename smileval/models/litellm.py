from .base import ChatCompletionModel, ChatMessage, ChatCompletionOptions, default_options

from litellm import acompletion

class LiteLLMChatCompletionModel(ChatCompletionModel):
    async def chat_complete(self, messages: list[ChatMessage], options: ChatCompletionOptions = default_options) -> ChatMessage:
        completions = await acompletion(model = self.name, messages = ChatMessage.to_api_format(messages))
        return ChatMessage.from_dict(completions['choices'][0]['message'])