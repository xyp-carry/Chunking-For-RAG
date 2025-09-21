from tokenize import group
from wxauto import WeChat
from wxauto.msgs import FriendMessage
from pypinyin import pinyin, Style
from autoqueue.redisMq import RedisQueue
from wxauto import WeChat
from wxauto.msgs import FriendMessage
import json
import time
import signal
import llm.Prompt as Prompt
from database.mysql_manager import MYSQL_Manage

class DCwx():
    def __init__(self, group_name = 'robot_test'):
        self.weClient = WeChat()
        self.group_name = group_name
        self.Mysql_database_name = 'wxhistory'
        self.judge_len = 3
        self.Mysql_user = 'root'
        self.Mysql_passwords = '123456'
        self.monitor_name = ''.join([i[0] for i in pinyin(self.weClient.nickname, style=Style.NORMAL)])
        self.Mysql_client = MYSQL_Manage(username = self.Mysql_user, passwords=self.Mysql_passwords, database_name=self.Mysql_database_name,table_name =self.monitor_name)

    

    def get_message(self, Searchname):
        '''
        获取此时窗口的对话信息
        '''
        return [(msg.sender,msg.content) for msg in self.weClient.core._get_chatbox(Searchname).get_msgs()]
    
    def set_group_name(self, group_name):
        self.group_name = group_name
    

    def moniter(self):
        '''
        该函数为监控微信的启动部分
        '''
        group_pinyin = ''.join([i[0] for i in pinyin(self.group_name, style=Style.NORMAL)])
        print('wxqueue' + group_pinyin)
        wxqueue = RedisQueue('wxqueue' + group_pinyin)
        # 可能出现群里没有历史记录
        local_history = self.get_check_point()
        print(len(local_history))
        try:
            if len(local_history) == 0:
                self.get_message(self.group_name)
                self.weClient.LoadMoreMessage(10)
                res = self.get_message(self.group_name)
                self.add_queue(wxqueue, res)
            else:
                
                [wxqueue.rput(json.dumps((r['user'],r['content']))) for r in local_history]
                res = self.get_message(self.group_name)
                self.weClient.LoadMoreMessage(5)
                res = self.get_message(self.group_name)
                fres = self.find_sam(wxqueue, res)
        
                if fres == False:
                    wxqueue.delete()
                    [wxqueue.rput(json.dumps((res[i][0], res[i][1]))) for i in range(0, len(res))]
                
        except:
            pass
        
        while wxqueue.qsize() > 50:
            wxqueue.get_nowait()

        
        def cleanup(mysql, redis):
            def signal_handler(signum, frame):
                print(f"接收到信号 {signum}，执行清理...")
                insert_data = []
                for i in range(3):
                    insert_data.append({'user':json.loads(redis.get_data(redis.qsize() - 3 + i))[0], 'content':json.loads(redis.get_data(redis.qsize() - 3 + i))[1],'group_name':self.group_name})
                mysql.Insert_database(insert_data)
                import sys
                sys.exit(0) 
            return signal_handler

        def on_message(msg, chat):
            if isinstance(msg, FriendMessage):
                time.sleep(2)
                if "@" + self.weClient.nickname == msg.content[0:len(self.weClient.nickname)+1]:
                    # answer = self.chat(qtype='custom',
                    #                     stream=False, 
                    #                     prompt=Prompt.RAG_PROMPT, 
                    #                     question=Prompt.RAG_USER, 
                    #                     arg_dict={
                    #                         'chunks':"".join(a.chunk_search(index="os_qa_pizza", question=msg.content[1+len(self.weClient.nickname):])[1]),
                    #                         'question':msg.content[1+len(self.weClient.nickname):]},
                    #                         )

                    # msg.quote(json.loads(answer.to_json())['choices'][0]['message']['content'])
                    msg.quote(json.loads('hello'))

        handler = cleanup(self.get_Mysql(), wxqueue)

        self.weClient.AddListenChat(nickname=self.group_name, callback=on_message)
        signal.signal(signal.SIGINT, handler)
        signal.signal(signal.SIGTERM, handler)
        self.weClient.KeepRunning()


    def get_check_point(self):
        '''
        获取本地记录的信息点
        '''
        mysql = self.Mysql_client
        mysql.init_table({'user':'', 'content':'', 'group_name':''})
        query = f"SELECT * FROM {self.monitor_name} where group_name = '{self.group_name}' limit 5"
        local_history = mysql.query_database(query=query)
        return local_history
    
    
    def add_queue(self, queue:RedisQueue, data):
        '''
        添加数据进入队列
        '''
        for r in data:
            if queue.qsize() >= 50:
                break
            queue.rput(json.dumps((r[0],r[1])))
        return True
    

    def find_sam(self, queue:RedisQueue, data):
        '''
        查询是否有符合本地记录点的对话信息，并进行同步
        '''
        for index, r in enumerate(data[self.judge_len:]):
            moniter = json.loads(queue.get_data(2))
            if r[0] == moniter[0] and r[1] == moniter[1]:
                moniter1 = json.loads(queue.get_data(1))
                moniter2 = json.loads(queue.get_data(0))
                if data[index-1][0] == moniter1[0] and data[index-1][1] == moniter1[1] and data[index-2][0] == moniter2[0] and data[index-2][1] == moniter2[1]:
                    [queue.rput(json.dumps((data[i][0], data[i][1]))) for i in range(index+1, len(data))]
                    return True
        return False

    def get_Mysql(self):
        return self.Mysql_client


# a = DCwx()
# print(a.moniter())