from llm.LLMs import LLMs
import llm.Prompt as Prompt
import json
from docx import Document
from tqdm import tqdm

from database.es_searcher import ES_Search

from DChandler.DCwx import DCwx


class Base_RAG():
    def __init__(
            self, 
            data_path: str = "http://localhost:9200", 
            database: str = 'elasticsearch',
            base_url:str = 'https://open.bigmodel.cn/api/paas/v4/', 
            api_key:str = '', 
            model:str = 'glm-4-flash-250414', 
            _async:bool = True
        ):
        self.data_path = data_path
        self.database = database 
        self._async = _async
        self.llm = LLMs(api_key= api_key,base_url = base_url, model = model, _async = _async)
        if self.database not in ['elasticsearch']:
            raise TypeError("数据库类型仅支持[elasticsearch]")
        if self.database == 'elasticsearch':
           self.search_client = ES_Search(data_path, self.database)

    #进行对话(异步模式)
    async def Asycchat(
            self, 
            question: str, 
            qtype:str = 'normal', 
            prompt:str = "", 
            arg_dict:dict = {}, 
            stream:str=True
        ):
        respose = await self.llm.Asycchat(question = question, 
                                          qtype=qtype, 
                                          prompt = prompt,
                                          stream = stream, 
                                          arg_dict = arg_dict)
        await respose

    #进行对话(同步模式)
    def chat(self, question: str, qtype:str = 'normal', prompt:str = "", arg_dict:dict = {}, stream:str=True):
        respose = self.llm.chat(question = question, qtype=qtype, prompt = prompt,stream = stream, arg_dict = arg_dict)
        return respose
    

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
    

    def connectwx(self, group_name):
        a = DCwx(group_name='返娘家')
        print("退出可按Ctrl + c, 如果没有找到对应的群，请关闭所有微信窗口重试或检查微信版本是否低于4.0")
        a.moniter()



a = Base_RAG(api_key="71f9c7ff218f8f7329a95c794a42c149.SfLL8ycOqirgYmvd", _async=False)
print(a.connectwx(group_name='返娘家'))


# chunk = a.file_split(filepath = "./FILE/oo.docx")
# a.connect_wx("robot_test","test_robot")


# import asyncio
# docs = a.chunk_search(index = 'os_qa_pizza', question ="什么是操作系统")[1]
# asyncio.run(a.chat("什么是操作系统",docs))
# print(a.get_index())
