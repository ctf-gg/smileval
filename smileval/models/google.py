from .base import ChatCompletionModel, ChatMessage, ChatCompletionOptions, EmbeddingModel, default_options, unsystem_prompt_chain
from ..utils import map_attribute

import os
# old code
# import google.generativeai as genai
from google import genai
from google.genai import types

google_role_conversion = {
    "assistant": "model",
    "user": "user",
    "system": "user"
}


# this is how the old method of disabling safety controls worked
#SAFETY_CATEGORIES = ["SEXUALLY_EXPLICIT", "HATE_SPEECH", "HARASSMENT", "DANGEROUS_CONTENT"]

#SAFETY_SETTINGS_NETURALIZATION = {}
#for category in SAFETY_CATEGORIES:
#    SAFETY_SETTINGS_NETURALIZATION[category] = "block_none"

class GoogleGenAIChatCompletionModel(ChatCompletionModel):
    def __init__(self, name: str, api_key: str | None = None, safety: bool = True):
        super().__init__(name)
        opts = {}
        if os.getenv("GOOGLE_GENAI_API_KEY"):
            opts["api_key"] = os.getenv("GOOGLE_GENAI_API_KEY")
        if api_key:
            opts["api_key"] = api_key

        # genai.configure(api_key = opts["api_key"])
        self.client: genai.GenerativeModel = genai.Client(api_key = opts["api_key"])
        self.opts = opts
        self.safety: bool = safety

    @staticmethod
    def convert_to_google_format(message: ChatMessage):
        return types.Content(
            role  =  google_role_conversion[message.role],
            parts = [types.Part.from_text(text=message.content)]
        )


    @staticmethod
    def map_to_google_format(chain: list[ChatMessage]) -> (None | str, list[dict]):

        rewritten = chain[:]
        system_message_content = None

        if len(rewritten) > 0 and rewritten[0].role == "system":
            system_message_content = rewritten.pop().content

        return system_message_content, [
            GoogleGenAIChatCompletionModel.convert_to_google_format(chat_msg) for chat_msg in rewritten   
        ]

    async def chat_complete(self, messages: list[ChatMessage], options: ChatCompletionOptions = default_options) -> ChatMessage:
        super().chat_complete_log_request(messages, options)
        messages, options = super().preprocess_inputs(messages, options)

        # old
        # gc_kwargs = {}
        generate_content_kwargs = {}
        generation_config_kwargs = {}

        map_attribute(options, generation_config_kwargs, "temperature", "temperature")
        map_attribute(options, generation_config_kwargs, "stop_tokens", "stop_sequences")
        map_attribute(options, generation_config_kwargs, "max_tokens", "max_output_tokens")
        
        map_attribute(options, generation_config_kwargs, "top_p", "top_p")
        map_attribute(options, generation_config_kwargs, "top_k", "top_k")

        system_message, chat_messages = GoogleGenAIChatCompletionModel.map_to_google_format(messages)
        
        if not self.safety:
            # generate_content_kwargs["safety_settings"] = SAFETY_SETTINGS_NETURALIZATION
            generation_config_kwargs["safety_settings"] = [
                types.SafetySetting(
                    category=types.HarmCategory.HARM_CATEGORY_CIVIC_INTEGRITY,
                    threshold=types.HarmBlockThreshold.BLOCK_NONE,
                ),
                types.SafetySetting(
                    category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                    threshold=types.HarmBlockThreshold.BLOCK_NONE,
                ),
                types.SafetySetting(
                    category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                    threshold=types.HarmBlockThreshold.BLOCK_NONE,
                ),
                types.SafetySetting(
                    category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                    threshold=types.HarmBlockThreshold.BLOCK_NONE,
                ),
                types.SafetySetting(
                    category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                    threshold=types.HarmBlockThreshold.BLOCK_NONE,
                ),
                #types.SafetySetting(
                #    category=types.HarmCategory.HARM_CATEGORY_UNSPECIFIED,
                #    threshold=types.HarmBlockThreshold.BLOCK_NONE,
                #)
            ]

        if system_message:
            generation_config_kwargs["system_instruction"] = system_message

        generation_config = types.GenerateContentConfig(**generation_config_kwargs)

        # old version
        # config = genai.types.GenerationConfig(**gc_kwargs)
        
        response = self.client.models.generate_content(contents = chat_messages, model = self.name, config = generation_config, **generate_content_kwargs)

        if response.candidates[0].safety_ratings:
            print(response.candidates[0].safety_ratings)

        completion_message = ChatMessage(response.text, role = "assistant").mark_as_generated()
        super().chat_complete_log_response(completion_message.content)
        return completion_message
