from elasticsearch import Elasticsearch
from LLMs import  LLMs
class Base_RAG():
    def __init__(self, data_path: str = "http://localhost:9200", index_name:str = '', database: str = 'elasticsearch',LLM:str = 'ZhipuAI', api_key:str = ''):
        self.data_path = data_path
        self.index_name = index_name
        self.database = database 
        self.llm = LLMs(LLM = LLM, api_key= api_key)
        if self.database not in ['elasticsearch']:
            raise TypeError("数据库类型仅支持[elasticsearch]")
        if self.database == 'elasticsearch':
           self.cilent = Elasticsearch(data_path)
        if self.index_name == '':
            raise TypeError("索引不能为空")
        

    def connection(self):
        if self.cilent.ping():
            print( "✓ ping测试成功")
            return True
        else:
            print('无法连接elasticsearch')
            return False
        

    def chunk_insert(self, data:dict):
        self.cilent.index(index = self.index_name, document=data)

    
    def chat(self, question: str, docs: list):
        return self.llm.chat(question)



