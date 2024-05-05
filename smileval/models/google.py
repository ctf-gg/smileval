from .base import ChatCompletionModel, ChatMessage, ChatCompletionOptions, EmbeddingModel, default_options, unsystem_prompt_chain
from ..utils import map_attribute

import google.generativeai as genai

google_role_conversion = {
    "assistant": "model",
    "user": "user",
    "system": "user"
}

class GoogleGenAIChatCompletionModel(ChatCompletionModel):
    def __init__(self, name: str, api_key: str | None = "sk-placeholder"):
        super().__init__(name)
        opts = {}
        if os.getenv("GOOGLE_GENAI_API_KEY"):
            opts["api_key"] = os.getenv("GOOGLE_GENAI_API_KEY")
        if api_key:
            opts["api_key"] = api_key

        genai.configure(api_key = opts["api_key"])
        self.model: genai.GenerativeModel = genai.GenerativeModel(name)
        self.opts = opts

    @staticmethod
    def convert_to_google_format(message: ChatMessage):
        return {
            "role": google_role_conversion[message.role],
            "parts": [message.content]
        }

    @staticmethod
    def map_to_google_format(chain: list[ChatMessage]) -> list[dict]:
        rewritten = unsystem_prompt_chain(chain)
        return [
            GoogleGenAIChatCompletionModel.convert_to_google_format(chat_msg) for chat_msg in rewritten   
        ]

    async def chat_complete(self, messages: list[ChatMessage], options: ChatCompletionOptions = default_options) -> ChatMessage:
        super().chat_complete_log_request(messages, options)
        messages, options = super().preprocess_inputs(messages, options)

        gc_kwargs = {}
        map_attribute(options, gc_kwargs, "temperature", "temperature")
        map_attribute(options, gc_kwargs, "stop_tokens", "stop_sequences")
        map_attribute(options, gc_kwargs, "max_tokens", "max_output_tokens")

        config = genai.types.GenerationConfig(**gc_kwargs)
        
        response = self.model.generate(GoogleGenAIChatCompletionModel.map_to_google_format(messages))

        completion_message = ChatMessage(response.text, role = "assistant").mark_as_generated()
        super().chat_complete_log_response(completion_message.content)
        return completion_message