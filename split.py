# coding=utf-8

class Episode():
    def __init__(self, filename):
        '''
        简单格式的剧本场景信息的切割
        :param session_content: 切割好的一场的所有内容
        '''
        self.filename = filename
        self.script = ''
        self.episodeList = []
        self.sessionList = []

        self.readScriptFile()
        self.splitEpisode()
        self.splitSession()
        # delete empty session in sessionList
        for s in self.sessionList:
            if len(s.sessionContent) == 0:
                self.sessionList.remove(s)
        self.showInfo()

    def readScriptFile(self):
        print('读取剧本')
        with open(self.filename, "r", encoding='gb18030') as f:  # 打开文件
            self.script = f.read()  # 读取文件

    def splitEpisode(self):
        print("分割集数")
        # p = re.compile(r'第\d+集')
        split_script = self.script.split('\n\n\t\t\t')
        for s in split_script:
            self.episodeList.append(s)

    def splitSession(self):
        episodeNum = 0
        for s in self.episodeList:
            splitSession = s.split(
                '\n********************************************************************************\n')
            sessionNum = 0
            for ss in splitSession:
                charactor = {}
                dialogue = []
                backgroud = []
                if len(ss) < 20:
                    continue
                # 解决台词换行问题
                ss = ss.replace('\n      ', "").replace('\n     ', "")
                # 开始切分数据
                ss = ss.split('\n')
                for line in ss:
                    line = line.replace('：', ":").replace(' ', '').replace('\n', '').replace('\t', '')
                    line = line.replace(' ', '')
                    line = line.replace(' ', '')
                    if '简介' in line:
                        summary = line.split('简介:')[1]
                        continue
                    elif ':' in line:
                        person = line.split(':')[0]
                        charactor.setdefault(person, 0)
                        charactor[person] += 1
                        dialogue.append(line.split(':')[1])

                self.sessionList.append(Session(episodeNum, sessionNum, summary, charactor, ss))
                sessionNum = sessionNum + 1

            episodeNum = episodeNum + 1

    def showInfo(self):
        for s in self.sessionList:
            print(s.episodeNum)
            print(s.sessionContent)
            if len(s.sessionContent) < 5:
                print(s.episodeNum)
                print(s.sessionContent)

    def cleanSession(self):
        for session in self.sessionListDirty:
            session = session.split('\n')
            for line in session:
                line = line.replace('：', ":").replace(' ', '').replace('\n', '')
                line = line.replace(' ', '')
                line = line.replace(' ', '')
                if '简介' in line:
                    summary = line.split('简介:')[1]
                elif ':' in line:
                    charactor = line.split(':')[0]
                    dialogue = line.split(':')[1]
                else:
                    backgroud = line

class Session():
    def __init__(self, episodeNum, sessionNum, summary, charactor, sessionContent):
        '''
        简单格式的剧本场景信息的切割
        :param session_content: 切割好的一场的所有内容
        episodeNum: 剧集编号
        sessionNum: 场景编号
        summary: 剧集简介
        charactor: 场景演员表
        '''
        self.episodeNum = 0
        self.sessionNum = 0
        """self.sessionBeginTime = ''
        self.sessionEndTime = ''"""
        self.summary = ''
        self.sessionLocation = ''
        self.charactor = {}
        self.mainEmotion = ''
        self.dialogueList = []
        self.sessionContent = ''
        self.dialogueSplitFlag = []

        self.episodeNum = episodeNum
        self.sessionNum = sessionNum
        self.summary = summary
        self.charactor = charactor
        self.sessionContent = sessionContent
        self.cleanSession()
        self.splitDialogue()

    def cleanSession(self):
        # 去除集数和简介信息
        for i in range(len(self.sessionContent)-1, -1, -1):
            if '第' in self.sessionContent[i] and '集' in self.sessionContent[i]:
                self.sessionContent.pop(i)
                continue
            elif '简介' in self.sessionContent[i] or '提供' in self.sessionContent[i] or '编剧' in self.sessionContent[i]:
                self.sessionContent.pop(i)

    def splitDialogue(self):
        for i in range(len(self.sessionContent)):
            if '（' in self.sessionContent[i] and '）' in self.sessionContent[i] and '上' in self.sessionContent[i]:
                self.dialogueSplitFlag.append(i)
                continue
            elif '（' in self.sessionContent[i] and '）' in self.sessionContent[i] and '对' in self.sessionContent[i]:
                self.dialogueSplitFlag.append(i)
                continue
            elif '：' in self.sessionContent[i] or ':' in self.sessionContent[i]:
                continue
            else:
                self.dialogueSplitFlag.append(i)





class Dialogue():
    def __init__(self, episodeNum, sessionNum, summary, charactor, dialogueContent):
        '''
        将一个场景分割为多段对话
        :param session_content: 切割好的一段对话的所有内容
        '''
        self.beginTime = ''
        self.endTime = ''
        self.summary = ''
        self.sessionLocation = ''
        self.charactor = {}
        self.mainEmotion = ''
        self.lineList = []
        self.sessionContent = ''

if __name__ == '__main__':
    episode = Episode('1.txt')
    print(episode)
