# coding=utf-8
import re
import datetime
import argparse, os, logging, time
logger = logging.getLogger(__name__)
class Episode():
    def __init__(self, args):
        self.args = args
        self.episodeList = []
        self.sessionList = []

        self.readEpisode()
        self.splitSession()
        # delete empty session in sessionList
        for s in self.sessionList:
            if len(s.sessionContent) == 0:
                self.sessionList.remove(s)

    def readEpisode(self):
        dir = self.args.scripts
        for root, dirs, files in os.walk(dir):
            for i in files:
                with open(dir+i, "r", encoding='UTF-8') as f:
                    self.episodeList.append(f.read())


    def splitSession(self):
        episodeNum = 0
        for s in self.episodeList:
            # clean the script
            s = s.replace('’', '\'')
            s = s.replace('\n\n', '\n').replace('’', '\'')
            # 剧本字幕统一表达
            s = s.replace('Lesley', 'Leslie')
            s = s.replace('mum', 'mom')
            splitSession = s.split('Scene:')
            while "" in splitSession:
                splitSession.remove("")
            sessionNum = 0

            for ss in splitSession:
                charactor = {}
                ss = ss.split('\n')
                while "" in ss:
                    ss.remove("")
                sessionLocation = ss[0]
                ss.pop(0)
                for line in ss:
                    if 'Scene:' in line:
                        continue
                    elif ':' in line:
                        person = line.split(':')[0]
                        charactor.setdefault(person, 0)
                        charactor[person] += 1
                self.sessionList.append(Session(episodeNum, sessionNum, charactor, ss, sessionLocation))
                sessionNum = sessionNum + 1
            episodeNum = episodeNum + 1

    def showInfo(self):
        print('Sum of session%d' %len(self.sessionList))


class Session():
    def __init__(self, episodeNum, sessionNum, charactor, sessionContent, sessionLocation):
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
        self.beginTimeBlockNum = None
        self.endTimeBlockNum = None
        self.sessionBeginTime = ''
        self.sessionEndTime = ''
        self.summary = ''
        self.sessionLocation = sessionLocation
        self.charactor = {}
        self.mainEmotion = ''
        self.dialogueList = []
        self.sessionContent = ''
        self.dialogueSplitFlag = []

        self.episodeNum = episodeNum
        self.sessionNum = sessionNum
        self.charactor = charactor
        self.sessionContent = sessionContent
        """self.cleanSession()
        self.splitDialogue()"""

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

        for f in range(len(self.dialogueSplitFlag) - 1):
            self.dialogueList.append(Dialogue(self.sessionContent[self.dialogueSplitFlag[f]:self.dialogueSplitFlag[f+1]]))


class Dialogue():
    def __init__(self, dialogueContent):
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
        self.dialogueContent = ''

        #self.summary = summary
        self.dialogueContent = dialogueContent

class Subtitle():
    def __init__(self, args):
        self.args = args
        self.subtitleList = []
        self.timeBlockList = []
        self.readSubtitle()
        self.splitSubtitle()
        self.setTimeBlockNum()
        self.timeBlockLen = len(self.timeBlockList)

    def readSubtitle(self):
        dir = self.args.subtitle
        for root, dirs, files in os.walk(dir):
            for i in files:
                with open(dir+i, "r", encoding='gb18030') as f:
                    self.subtitleList.append(f.read())

    def splitSubtitle(self):
        episodeNum = 0
        for s in self.subtitleList:
            # clean the subtitle
            timeBlock = s.split('\n\n')
            while "" in timeBlock:
                timeBlock.remove("")
            for ss in timeBlock:
                ss = ss.split('\n')
                while "" in ss:
                    ss.remove("")
                if len(ss) == 4:
                    beginTime, endTime = ss[1].split('-->')
                    content_zh = ss[2]
                    content_en = ss[3].lower()
                    self.timeBlockList.append(
                        TimeBlock(episodeNum, beginTime, endTime, content_zh, content_en))
                # Find time
                else:
                    continue
            episodeNum = episodeNum + 1

    def setTimeBlockNum(self):
        for i in range(len(self.timeBlockList)):
            self.timeBlockList[i].timeBlockNum = i

class TimeBlock():
    def __init__(self, episodeNum, beginTime, endTime, content_zh, content_en):
        self.timeBlockNum = 0
        self.episodeNum = episodeNum
        self.beginTime = beginTime
        self.endTime = endTime
        self.content_zh = content_zh
        self.content_en = content_en

def parse_config():
    parser = argparse.ArgumentParser()

    # IO
    parser.add_argument('--scripts', type=str, default='../script/corpus/S01/scripts/')
    parser.add_argument('--subtitle', type=str, default='../script/corpus/S01/subtitle/')
    parser.add_argument('--video', type=str, default='../script/corpus/S01/video/')
    parser.add_argument('--output', type=str, default='../script/corpus/S01/split/')

    return parser.parse_args()

# 全字匹配
def isIncludeKeyWord(detailinfo, keyword):
  if -1 != detailinfo.find(keyword):
    pattern_str = '(^' + keyword + '$)|(^' + keyword + '(\W+).*)|(.*(\W+)' + keyword + '$)|(.*(\W+)' + keyword + '(\W+).*)'
    m = re.match(r'' + pattern_str + '', detailinfo)
    if m:
      return 1
  return 0

# 字幕时间相减 srt2 > srt1
def time_differ(date1, date2):
    date1 = date1.strip()
    date2 = date2.strip()
    date1 = re.sub(r',[0-9 ]+', '', date1)
    date2 = re.sub(r',[0-9 ]+', '', date2)
    '''
    @传入是时间格式如'12:55:05'
    '''
    date1 = datetime.datetime.strptime(date1, "%H:%M:%S")
    date2 = datetime.datetime.strptime(date2, "%H:%M:%S")
    if date1 < date2:
        return (date2 - date1).total_seconds()
    else:
        return (date1 - date2).total_seconds()


def LocateTime(episode, subtitle):
    # 已完成定位的段落将不再参与之后的定位
    flag = 0
    for s in episode.sessionList:
        episodeNum = s.episodeNum
        sessionNum = s.sessionNum
        alternate = []
        for sub in subtitle.timeBlockList:
            if sub.episodeNum == episodeNum and sub.timeBlockNum >= flag:
                alternate.append(sub)
            elif sub.episodeNum > episodeNum:
                break
            else:
                continue
        # locate begin
        i = 0
        while ':' not in s.sessionContent[i]:
            i = i + 1
        beginCharactor, beginContent1 = s.sessionContent[i].split(':')

        m = i + 1
        if m >= len(s.sessionContent) - 1:
            beginContent = beginContent1
        else:
            while ':' not in s.sessionContent[m]:
                m = m + 1
            _, beginContent2 = s.sessionContent[m].split(':', 1)
            beginContent = beginContent1 + beginContent2


        # 定位结尾
        j = len(s.sessionContent) - 1
        while True:
            if ':' in s.sessionContent[j] or j == 0:
                endCharactor, endContent1 = s.sessionContent[j].split(':')
                break
            else:
                j = j - 1

        n = j - 1
        while True:
            if ':' in s.sessionContent[n] or n == 0:
                _, endContent2 = s.sessionContent[n].split(':')
                break
            else:
                n = n - 1
        endContent = endContent2 + endContent1

        #beginContent = re.sub('\(.*?\)', '', beginContent)
        beginContent = beginContent.lower()
        #beginContent = max(beginContent, key=len, default='').lower().strip()

        #endContent = re.sub('\(.*?\)', '', endContent)
        endContent = endContent.lower()
        #endContent = max(endContent, key=len, default='').lower().strip()

        beginTime = None
        endTime = None
        timeBlockNum1 = timeBlockNum2 = None
        for i in range(len(alternate)):
            if i == len(alternate) - 1:
                _srt = re.split(r'[-.,?!"]', alternate[i].content_en)
                srt = max(_srt, key=len, default='').lower().strip()
                if isIncludeKeyWord(beginContent, srt):
                    beginTime = alternate[i].beginTime
                    timeBlockNum1 = alternate[i].timeBlockNum
                    # 完成开头定位的片段将不参与之后的结尾定位
                    alternate = alternate[i:]
                    break
            else:
                _srt = re.split(r'[-.,?!"]', alternate[i].content_en)
                _next = re.split(r'[-.,?!"]', alternate[i+1].content_en)
                srt_next = max(_next, key=len, default='').lower().strip()
                srt = max(_srt, key=len, default='').lower().strip()
                if isIncludeKeyWord(beginContent, srt) and isIncludeKeyWord(beginContent, srt_next):
                    beginTime = alternate[i].beginTime
                    timeBlockNum1 = alternate[i].timeBlockNum
                    # 完成开头定位的片段将不参与之后的结尾定位
                    alternate = alternate[i:]
                    break

        j = len(alternate) - 1
        while True:
            if j == 0:
                break
            else:
                _srt = re.split(r'[-.,?!"]', alternate[j].content_en)
                _next = re.split(r'[-.,?!"]', alternate[j - 1].content_en)
                srt_next = max(_next, key=len, default='').lower().strip()
                srt = max(_srt, key=len, default='').lower().strip()
                if isIncludeKeyWord(endContent, srt) and isIncludeKeyWord(endContent, srt_next):
                    endTime = alternate[j].endTime
                    timeBlockNum2 = alternate[j].timeBlockNum
                    flag = alternate[j].timeBlockNum
                    j = j - 1
                else:
                    j = j - 1


        if timeBlockNum2 and timeBlockNum1 and timeBlockNum2 > timeBlockNum1:
            s.sessionBeginTime = beginTime
            s.beginTimeBlockNum = timeBlockNum1
            s.sessionEndTime = endTime
            s.endTimeBlockNum = timeBlockNum2
        elif timeBlockNum1:
            s.sessionBeginTime = beginTime
            s.beginTimeBlockNum = timeBlockNum1
        elif timeBlockNum2:
            s.sessionEndTime = endTime
            s.endTimeBlockNum = timeBlockNum2
        else:
            continue
    # manual set time
    setTime(episode, subtitle)
    # if current session doesn't have begin-time or end-time, search the session before or after,
    # according to the continuity of time-block, set the begin-time or end-time
    for i in range(len(episode.sessionList)-1):
        if episode.sessionList[i].beginTimeBlockNum is None and episode.sessionList[i-1].endTimeBlockNum:
            episode.sessionList[i].sessionBeginTime = subtitle.timeBlockList[episode.sessionList[i-1].endTimeBlockNum+1].beginTime
            episode.sessionList[i].beginTimeBlockNum = subtitle.timeBlockList[episode.sessionList[i-1].endTimeBlockNum+1].timeBlockNum
        if episode.sessionList[i].endTimeBlockNum is None and episode.sessionList[i+1].beginTimeBlockNum:
            episode.sessionList[i].sessionEndTime = subtitle.timeBlockList[episode.sessionList[i+1].beginTimeBlockNum-1].beginTime
            episode.sessionList[i].endTimeBlockNum = subtitle.timeBlockList[episode.sessionList[i+1].beginTimeBlockNum-1].timeBlockNum

def setTime(episode,subtitle):
    dic = {}
    for s in subtitle.timeBlockList:
        temp = {s.beginTime: s.timeBlockNum}
        dic.update(temp)

    episode.sessionList[-1].sessionEndTime = subtitle.timeBlockList[-1].beginTime
    episode.sessionList[-1].endTimeBlockNum = len(subtitle.timeBlockList)
    episode.sessionList[158].sessionBeginTime = '00:19:19,920 '
    episode.sessionList[158].beginTimeBlockNum = dic[episode.sessionList[158].sessionBeginTime]

# 打印定位的置信度：定位前后三句话覆盖的单词比例
def printConfidence(episode, subtitle):
    reg = "[-.,?!\"]"
    for e in episode.sessionList:
        # 开头置信度计算
        content = e.sessionContent
        srt = subtitle.timeBlockList[e.beginTimeBlockNum].content_en
        srt1 = subtitle.timeBlockList[e.beginTimeBlockNum + 1].content_en
        srt2 = subtitle.timeBlockList[e.beginTimeBlockNum + 2].content_en
        srt3 = subtitle.timeBlockList[e.beginTimeBlockNum + 3].content_en
        #content = re.sub(reg, '', content)
        srt = re.sub(reg, '', srt)
        srt1 = re.sub(reg, '', srt1)
        srt2 = re.sub(reg, '', srt2)
        srt3 = re.sub(reg, '', srt3)



def main(args):

    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s -   %(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S',
                        level=logging.INFO)
    logger.info('Collecting data...')

    episode = Episode(args)

    subtitle = Subtitle(args)


    LocateTime(episode, subtitle)
    flag1 = 0
    flag2 = 0
    flag3 = 0
    noBegin = []
    noEnd = []
    for i in range(len(episode.sessionList)):
        if episode.sessionList[i].sessionBeginTime:
            flag1 = flag1 + 1
        else:
            noBegin.append(i)
        if episode.sessionList[i].sessionEndTime:
            flag2 = flag2 + 1
        else:
            noEnd.append(i)
        if episode.sessionList[i].sessionBeginTime and episode.sessionList[i].sessionEndTime:
            flag3 = flag3 + 1
    episode.showInfo()
    print(flag1, flag2, flag3)
    for i in noBegin:
        print(episode.sessionList[i].episodeNum, episode.sessionList[i].sessionNum)
    print('\n')
    for i in noEnd:
        print(episode.sessionList[i].episodeNum, episode.sessionList[i].sessionNum)
    printConfidence(episode, subtitle)
if __name__ == '__main__':
    args = parse_config()
    main(args)