from .base import ChatCompletionModel, ChatMessage, ChatCompletionOptions, EmbeddingModel, default_options

from litellm import aembedding

class LiteLLMChatCompletionModel(ChatCompletionModel):
    async def chat_complete(self, messages: list[ChatMessage], options: ChatCompletionOptions = default_options) -> ChatMessage:
        super().chat_complete_log_request(messages, options)
        completions = await acompletion(model = self.name, messages = ChatMessage.to_api_format(messages))
        completion_message = completions['choices'][0]['message']
        super().chat_complete_log_response(completion_message)
        return ChatMessage.from_dict(completion_message)

class LiteLLMEmbeddingModel(EmbeddingModel):
    '''
    Not all LiteLLM supported services can generate embeddings for text however.
    '''
    async def embed(self, messages: str | list[str]) -> list[list[float]]:
        '''
        reference api format guessed from https://github.com/BerriAI/litellm/blob/main/litellm/tests/test_caching.py
        '''
        embedding_objects = await aembedding(self.name, input = messages)
        return [
            embedding_object["embedding"] for embedding_object in embedding_objects.data
        ]