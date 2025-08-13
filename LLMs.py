from zhipuai import ZhipuAI

# 目前仅支持智谱AI
class LLMs():
    def __init__(self, api_key:str = '', LLM:str = 'ZhipuAI', docs:list = []):
        self.api_key = api_key
        self.docs = '\n'.join(docs)
        if self.api_key == '':
            raise TypeError("api_key 不可以为空")
        print(api_key)
        self.client = ZhipuAI(api_key=api_key)
        #此处需要增加异常捕捉措施

    #目前是RAG的格式后续需要改成常规格式，prompt将作为单独模块进行设置
    def chat(self, question):
        response = self.client.chat.completions.create(
            model="glm-4-flash-250414",  # 请填写您要调用的模型名称
            messages=[
                {"role": "system", "content": f"用户想了解{question}。请先提炼问题的核心意思，然后结合以下知识库中的内容，给出最清晰、最准确的答案，如果没有问题的准确答案就回答:找不到准确答案，尽量减少其他多余回答"},
                {"role":"user", "content":f"文档为{self.docs}"}
            ],
            stream=True,
    )
        return response