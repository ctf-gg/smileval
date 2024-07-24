from .base import ChatCompletionModel, ChatMessage, ChatCompletionOptions, EmbeddingModel, default_options
from ..utils import map_attribute

from jinja2 import Environment, BaseLoader

import os
import openai
import requests
import json

# TODO: move this into base
def download_tokenizer(tokenizer_str):
    # support url only for now
    if tokenizer_str.startswith("http://") or tokenizer_str.startswith("https://"):
        response = requests.get(tokenizer_str.replace("/blob/", "/raw/")) # allows easily pasting tokenzier.json
        return json.loads(response.text)
    else:
        import tokenizers
        tokenizer = tokenizers.Tokenizer(tokenizer_str)
        # raise NotImplementedError("hf tokenizers not implemented.")
        return {
            # this is good enough for now?
            "chat_template": tokenizer.tokenizer_config_dict["chat_template"],
            "eos_token": tokenizer.tokenizer_config_dict["eos_token"],
        }

class OpenAIChatCompletionModel(ChatCompletionModel):
    def __init__(self, name: str, api_key: str | None = None, base_url: str | None = None, spoof_api_name: str | None = None, extended = False):
        super().__init__(name)
        opts = {}
        if os.getenv("OPENAI_BASE_URL"):
            opts["base_url"] = os.getenv("OPENAI_BASE_URL")
        if base_url:
            opts["base_url"] = base_url


        if os.getenv("OPENAI_API_KEY"):
            opts["api_key"] = os.getenv("OPENAI_API_KEY")
        if api_key:
            opts["api_key"] = api_key
        
        self.client = openai.AsyncOpenAI(**opts)
        self.opts = opts
        self.model_name = name
        if spoof_api_name:
            self.model_name = spoof_api_name
        self.is_extended: bool = extended

    async def chat_complete(self, messages: list[ChatMessage], options: ChatCompletionOptions = default_options) -> ChatMessage:
        super().chat_complete_log_request(messages, options)
        messages, options = super().preprocess_inputs(messages, options)
        openai_kwargs = {}
        map_attribute(options, openai_kwargs, "temperature", "temperature")
        map_attribute(options, openai_kwargs, "top_p", "top_p")
        map_attribute(options, openai_kwargs, "stop_tokens", "stop")
        map_attribute(options, openai_kwargs, "seed", "seed") # important
        map_attribute(options, openai_kwargs, "max_tokens", "max_tokens")
        extra_args = {}
        if self.is_extended:
            # Mirostat
            map_attribute(options, extra_args, "mirostat", "mirostat")
            map_attribute(options, extra_args, "mirostat_eta", "mirostat_eta")
            map_attribute(options, extra_args, "mirostat_tau", "mirostat_tau")
            # Alt names
            map_attribute(options, extra_args, "max_tokens", "n_predict")
            # sampling
            map_attribute(options, extra_args, "top_k", "top_k")
            map_attribute(options, extra_args, "min_p", "min_p")
        completions = await self.client.chat.completions.create(messages = ChatMessage.to_api_format(messages), model = self.model_name,extra_body = extra_args, **openai_kwargs)
        # types get funky here for some reason
        completion_message = ChatMessage(completions.choices[0].message.content, role = completions.choices[0].message.role).mark_as_generated()
        super().chat_complete_log_response(completion_message.content)
        return completion_message

class OpenAITextCompletionModel(ChatCompletionModel):
    def __init__(self, name: str, tokenizer: str, api_key: str | None = None, base_url: str | None = None, spoof_api_name: str | None = None, extended = False):
        super().__init__(name)
        opts = {}
        if os.getenv("OPENAI_BASE_URL"):
            opts["base_url"] = os.getenv("OPENAI_BASE_URL")
        if base_url:
            opts["base_url"] = base_url

        if os.getenv("OPENAI_API_KEY"):
            opts["api_key"] = os.getenv("OPENAI_API_KEY")
        if api_key:
            opts["api_key"] = api_key
        
        self.client = openai.AsyncOpenAI(**opts)
        self.opts = opts
        self.model_name = name
        if spoof_api_name:
            self.model_name = spoof_api_name
        self.is_extended: bool = extended
        self.tokenizer_str = tokenizer
        self.tokenizer = download_tokenizer(tokenizer)
        # TODO: make it so people can't rce here
        # surely no one is downloading a tokenizer with a virus?
        self.chat_template_env = Environment(loader = BaseLoader())
        self.chat_template = self.chat_template_env.from_string(self.tokenizer["chat_template"])

    def format_to_text(self, messages: list[ChatMessage]) -> str:
        # bos_token = tokenizer.bos_token, eos_token = tokenizer.eos_token
        def raise_exception(message):
            raise ValueError(message)
        return self.chat_template.render(messages = ChatMessage.to_api_format(messages),add_generation_prompt = True, raise_exception = raise_exception, len = len, str = str, int = int)        

    async def chat_complete(self, messages: list[ChatMessage], options: ChatCompletionOptions = default_options) -> ChatMessage:
        super().chat_complete_log_request(messages, options)
        messages, options = super().preprocess_inputs(messages, options)
        openai_kwargs = {}
        map_attribute(options, openai_kwargs, "temperature", "temperature")
        map_attribute(options, openai_kwargs, "top_p", "top_p")
        map_attribute(options, openai_kwargs, "stop_tokens", "stop")
        map_attribute(options, openai_kwargs, "seed", "seed") # important
        map_attribute(options, openai_kwargs, "max_tokens", "max_tokens")
        extra_args = {}
        if self.is_extended:
            # Mirostat
            map_attribute(options, extra_args, "mirostat", "mirostat")
            map_attribute(options, extra_args, "mirostat_eta", "mirostat_eta")
            map_attribute(options, extra_args, "mirostat_tau", "mirostat_tau")
            # Alt names
            map_attribute(options, extra_args, "max_tokens", "n_predict")
            # sampling
            map_attribute(options, extra_args, "top_k", "top_k")
            map_attribute(options, extra_args, "min_p", "min_p")

        prompt = self.format_to_text(messages)
        if os.getenv("SMILEVAL_LOG_COMPLETIONS"):
            print("=== LOG PROMPT ===")
            print(prompt)
            print("=== END LOG PROMPT ===")
        completions = await self.client.completions.create(prompt = prompt, model = self.model_name, extra_body = extra_args, **openai_kwargs)
        # chat completion api for refernece:
        # completions = await self.client.chat.completions.create(messages = ChatMessage.to_api_format(messages), model = self.model_name,extra_body = extra_args, **openai_kwargs)
        # types get funky here for some reason, counterintuitive type
        # print(completions)
        text: str = completions.content
        print(completions)
        # print(self.tokenizer["eos_token"])
        # if text.endswith(self.tokenizer["eos_token"]):
        #     text = text[:-len(self.tokenizer["eos_token"])]
        completion_message = ChatMessage(text, role = "assistant").mark_as_generated() # .choices[0].text
        super().chat_complete_log_response(completion_message.content)
        return completion_message

class OpenAIEmbeddingModel(EmbeddingModel):
    def __init__(self, name: str, api_key: str | None = "sk-placeholder", host: str | None = None, spoof_api_name: str | None = None):
        super().__init__(name)
        opts = {}
        if os.getenv("OPENAI_BASE_URL"):
            opts["base_url"] = os.getenv("OPENAI_BASE_URL")
        if host:
            opts["base_url"] = host


        if os.getenv("OPENAI_API_KEY"):
            opts["api_key"] = os.getenv("OPENAI_API_KEY")
        if api_key:
            opts["api_key"] = api_key
        
        self.client = openai.AsyncOpenAI(**opts)
        self.opts = opts
        self.model_name = name
        if spoof_api_name:
            self.model_name = spoof_api_name
    
    async def embed(self, messages: str | list[str]) -> list[list[float]]:
        raise NotImplemented("todo")