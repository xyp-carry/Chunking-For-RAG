from openai import AsyncOpenAI, OpenAI


class LLMs():
    def __init__(self, api_key:str = '', base_url:str = '', model:str='', _async:bool = True):
        self.api_key = api_key
        self._async = _async
        if self.api_key == '':
            raise TypeError("api_key 不可以为空")
        
        #异步调取模型服务端
        if self._async:
            self.client = AsyncOpenAI(
                api_key= self.api_key,
                base_url=base_url
            )
        else:
            self.client = OpenAI(
                api_key= self.api_key,
                base_url=base_url
            )
        
        if model == '':
            raise TypeError("模型名称不可为空")
        self.model = model
        #此处需要增加异常捕捉措施


    async def Asycchat(self, question:str, qtype:str, prompt:str = "" , arg_dict:dict = {},stream:bool=True):
        if self._async == False:
            raise ValueError("不可以在非异步模式下使用该函数")
        try:
            if qtype == 'normal':
                response = await self.client.chat.completions.create(
                    model= self.model,
                    messages=[
                        {"role":"user", "content":f"{question}"}
                    ],
                    stream=True
            )
            elif qtype == 'custom':
                response = await self.client.chat.completions.create(
                    model= self.model,
                    messages=[
                        {"role":"system", "content":f"{prompt.format_map(arg_dict)}"},
                        {"role":"user", "content":f"{question.format_map(arg_dict)}"}
                    ],
                    stream=stream
            )
        except Exception as e:
            raise TypeError(f"{e}")
        
        return response
    
    def chat(self, question:str, qtype:str, prompt:str = "" , arg_dict:dict = {},stream:bool=True):
        if self._async:
            raise ValueError("不可以在异步模式下使用该函数")
        try:
            if qtype == 'normal':
                response = self.client.chat.completions.create(
                    model= self.model,
                    messages=[
                        {"role":"user", "content":f"{question}"}
                    ],
                    stream=stream
            )
            elif qtype == 'custom':
                response = self.client.chat.completions.create(
                    model= self.model,
                    messages=[
                        {"role":"system", "content":f"{prompt.format_map(arg_dict)}"},
                        {"role":"user", "content":f"{question.format_map(arg_dict)}"}
                    ],
                    stream=stream
            )
        except Exception as e:
            raise TypeError(f"{e}")
        return response