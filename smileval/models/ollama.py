from .base import ChatCompletionModel, ChatMessage, ChatCompletionOptions, EmbeddingModel,default_options

import ollama
from ollama import AsyncClient

import os
import asyncio

from ..utils import map_attribute

class OllamaChatCompletionModel(ChatCompletionModel):
    def __init__(self, name: str, host: str | None = None):
        super().__init__(name)
        opts = {}
        if os.getenv("OLLAMA_HOST"):
            opts["host"] = os.getenv("OLLAMA_HOST")
        if host:
            opts["host"] = host
        self.client = AsyncClient(**opts)
    
    async def chat_complete(self, messages: list[ChatMessage], options: ChatCompletionOptions = default_options) -> ChatMessage:
        super().chat_complete_log_request(messages, options)
        messages, options = super().preprocess_inputs(messages, options)
        ollama_options = {}
        map_attribute(options, ollama_options, "temperature", "temperature")
        map_attribute(options, ollama_options, "stop_tokens", "stop")
        map_attribute(options, ollama_options, "seed", "seed")
        completion = await self.client.chat(model = self.name, messages = ChatMessage.to_api_format(messages), options = ollama_options)
        super().chat_complete_log_response(completion['message'])
        return ChatMessage.from_dict(completion['message']).mark_as_generated()

class OllamaEmbeddingModel(EmbeddingModel):
    def __init__(self, name: str, host: str | None = None):
        super().__init__(name)
        opts = {}
        if os.getenv("OLLAMA_HOST"):
            opts["host"] = os.getenv("OLLAMA_HOST")
        if host:
            opts["host"] = host
        self.client = AsyncClient(**opts)

    # are batch embeddings a thing? will be literally serial for now
    async def embed_one(self, message: str) -> list[float]:
        embedding = await self.client.embeddings(self.name, message)
        return embedding

    async def embed(self, messages: str | list[str]) -> list[list[float]]:
        coroutines = [
            self.embed_one(message) for message in messages
        ]
        embeddings = await asyncio.gather(*coroutines)
        return embeddings