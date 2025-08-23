from elasticsearch import Elasticsearch
from LLMs import  LLMs
import Prompt
import json
from docx import Document
from tqdm import tqdm

from wxauto import WeChat
from wxauto.msgs import FriendMessage
import time
class Base_RAG():
    def __init__(self, data_path: str = "http://localhost:9200", database: str = 'elasticsearch',base_url:str = 'https://open.bigmodel.cn/api/paas/v4/', api_key:str = '', model:str = 'glm-4-flash-250414', _async:bool = True):
        self.data_path = data_path
        self.database = database 
        self._async = _async
        self.llm = LLMs(api_key= api_key,base_url = base_url, model = model, _async = _async)
        if self.database not in ['elasticsearch']:
            raise TypeError("数据库类型仅支持[elasticsearch]")
        if self.database == 'elasticsearch':
           self.client = Elasticsearch(data_path)
        
    #检测是否能够连接数据库
    def connection_elasticsearch(self):
        if self.client.ping():
            print( "✓ ping测试成功")
            return True
        else:
            print('无法连接elasticsearch')
            return False
        
    #插入知识块(该部分需要增加检测机制)
    def chunk_insert(self, index:str,data:dict):
        self.client.index(index = index, document=data)

    #进行对话(异步模式)
    async def Asycchat(self, question: str, qtype:str = 'normal', prompt:str = "", arg_dict:dict = {}, stream:str=True):
        respose = await self.llm.Asycchat(question = question, qtype=qtype, prompt = prompt,stream = stream, arg_dict = arg_dict)
        await respose

    #进行对话(同步模式)
    def chat(self, question: str, qtype:str = 'normal', prompt:str = "", arg_dict:dict = {}, stream:str=True):
        respose = self.llm.chat(question = question, qtype=qtype, prompt = prompt,stream = stream, arg_dict = arg_dict)
        return respose

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

    # 提供文档切割的接口
    def file_split(self, filepath:str):
        if filepath.endswith('.docx'):
            file = Document(filepath)
            text = []
            chunk = []
            for element in tqdm(file.element.body):
                if element.tag.endswith('p'):
                    # 
                    arg = {
                        'documnet':''.join(text),
                        'sentence':element.text
                    }
                    res = self.chat(qtype = 'custom', prompt=Prompt.TITLE_IDENTIFICATION, question=Prompt.TITLE_IDENTIFICATION_USER,arg_dict = arg,stream = False)
                    if json.loads(res.to_json())['choices'][0]['message']['content'] == '正文':
                        text.append(element.text+'\n')
                    else:
                        chunk.append(''.join(text[:-1]))
                        text = []

                if element.tag.endswith('tbl'):
                    table_c = 0
                    for row in element.tr_lst:
                        for tc in row.tc_lst:
                            for p in tc.p_lst:
                                if table_c == 0:
                                    text.append(p.text+' | ')
                        text.append('\n')
            return chunk
        elif filepath.endswith('.pdf'):
            pass
        else:
            raise ValueError("文件只支持.docx、.pdf文件")

    def connect_wx(self, groupname:str = "",nickname:str = ""):
        def on_message(msg, chat):
            if isinstance(msg, FriendMessage):
                time.sleep(2)
                if "@" + nickname == msg.content[0:len(nickname)+1]:
                    answer = self.chat(qtype='custom',stream=False, prompt=Prompt.RAG_PROMPT, question=Prompt.RAG_USER, arg_dict={
    'chunks':"".join(a.chunk_search(index="os_qa_pizza", question=msg.content[1+len(nickname):])[1]),
    'question':msg.content[1+len(nickname):]
})
                    msg.quote(json.loads(answer.to_json())['choices'][0]['message']['content'])
        
        wx = WeChat()

        wx.AddListenChat(nickname=groupname, callback=on_message)

        wx.KeepRunning()

        

a = Base_RAG(api_key="71f9c7ff218f8f7329a95c794a42c149.SfLL8ycOqirgYmvd", _async=False)

# chunk = a.file_split(filepath = "./FILE/oo.docx")
a.connect_wx("robot_test","test_robot")


# import asyncio
# docs = a.chunk_search(index = 'os_qa_pizza', question ="什么是操作系统")[1]
# asyncio.run(a.chat("什么是操作系统",docs))
# print(a.get_index())