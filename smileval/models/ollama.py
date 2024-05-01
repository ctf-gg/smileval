from .base import ChatCompletionModel, ChatMessage, ChatCompletionOptions, default_options

import ollama
from ollama import AsyncClient

import os

class OllamaChatCompletionModel(ChatCompletionModel):
    def __init__(self, name: str):
        super().__init__(name)
        opts = {}
        if os.getenv("OLLAMA_HOST"):
            opts["host"] = os.getenv("OLLAMA_HOST")
        self.client = AsyncClient(**opts)
    
    async def chat_complete(self, messages: list[ChatMessage], options: ChatCompletionOptions = default_options) -> ChatMessage:
        completion = await self.client.chat(model = self.name, messages = ChatMessage.to_api_format(messages))
        return ChatMessage.from_dict(completion['message'])