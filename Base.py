from elasticsearch import Elasticsearch
from LLMs import  LLMs
class Base_RAG():
    def __init__(self, data_path: str = "http://localhost:9200", database: str = 'elasticsearch',base_url:str = 'https://open.bigmodel.cn/api/paas/v4/', api_key:str = '', model:str = 'glm-4-flash-250414'):
        self.data_path = data_path
        self.database = database 
        self.llm = LLMs(api_key= api_key,base_url = base_url, model = model)
        if self.database not in ['elasticsearch']:
            raise TypeError("数据库类型仅支持[elasticsearch]")
        if self.database == 'elasticsearch':
           self.client = Elasticsearch(data_path)
        
    #检测是否能够连接数据库
    def connection_elasticsearch(self):
        if self.cilent.ping():
            print( "✓ ping测试成功")
            return True
        else:
            print('无法连接elasticsearch')
            return False
        
    #插入知识块(该部分需要增加检测机制)
    def chunk_insert(self, index:str,data:dict):
        self.client.index(index = index, document=data)

    #进行对话
    async def chat(self, question: str, docs: list):
        respose = await self.llm.chat(question = question, Type='rag', docs = docs)
        async for item in respose:          
            print(item)

    #获取有哪些知识库
    def get_index(self):
        return [index for index in self.client.indices.get(index = "*")]
    
    #进行知识块搜索
    def chunk_search(self, index:str, question:str):
        docs = []
        ids = []
        query = {"query":{"bool":{"must":[{"match":{"content":question}}],"must_not":[],"should":[]}},"from":0,"size":10,"sort":[],"aggs":{}}
        response = self.client.search(index=index, body=query)
        if response['hits']['total']['value'] <= 10:
            for doc in response['hits']['hits']:
                docs.append(doc['_source']['content'])
                ids.append(doc['_id'])
        else:
            for i in range(10):
                docs.append(response['hits']['hits'][i]['_source']['content'])
                ids.append(response['hits']['hits'][i]['_id'])
        return ids, docs


# a = Base_RAG(api_key="71f9c7ff218f8f7329a95c794a42c149.SfLL8ycOqirgYmvd")
# import asyncio
# docs = a.chunk_search(index = 'os_qa_pizza', question ="什么是操作系统")[1]
# asyncio.run(a.chat("什么是操作系统",docs))
# print(a.get_index())