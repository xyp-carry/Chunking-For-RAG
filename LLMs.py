from openai import AsyncOpenAI


class LLMs():
    def __init__(self, api_key:str = '', base_url:str = '', docs:list = [], model:str=''):
        self.api_key = api_key

        if self.api_key == '':
            raise TypeError("api_key 不可以为空")
        
        #异步调取模型服务端
        self.client = AsyncOpenAI(
            api_key= self.api_key,
            base_url=base_url
        )
        print(self.api_key, base_url)
        if model == '':
            raise TypeError("模型名称不可为空")
        self.model = model
        #此处需要增加异常捕捉措施


    async def chat(self, question:str, Type:str, docs:list = []):
        try:
            if Type == 'rag':
                if len(docs) == 0:
                    raise ValueError("文档不可为空")
                response = await self.client.chat.completions.create(
                    model= self.model,
                    messages=[
                        {"role": "system", "content": f"用户想了解{question}。请先提炼问题的核心意思，然后结合以下知识库中的内容，给出最清晰、最准确的答案，如果没有问题的准确答案就回答:找不到准确答案，尽量减少其他多余回答"},
                        {"role":"user", "content":f"文档为{'\n'.join(docs)}"}
                    ],
                    stream=True
            )
            elif Type == 'normal':
                response = await self.client.chat.completions.create(
                    model= self.model,
                    messages=[
                        {"role":"user", "content":f"{question}"}
                    ],
                    stream=True
            )
        except Exception as e:
            raise TypeError(f"{e}")
        
        return response
    