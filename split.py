# coding=utf-8
import re
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
            s = s.replace('\n\n', '\n')
            # 剧本字幕不同人名问题
            s = s.replace('Lesley', 'Leslie')
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

def LocateTime(episode, subtitle):
    for s in episode.sessionList:
        episodeNum = s.episodeNum
        sessionNum = s.sessionNum
        alternate = []
        for sub in subtitle.timeBlockList:
            if sub.episodeNum == episodeNum:
                alternate.append(sub)
            elif sub.episodeNum > episodeNum:
                break
            else:
                continue

        # locate begin
        i = 0
        while ':' not in s.sessionContent[i]:
            i = i + 1
        beginCharactor, beginContent = s.sessionContent[i].split(':')

        j = len(s.sessionContent) - 1
        while True:
            if ':' in s.sessionContent[j] or j == 0:
                endCharactor, endContent = s.sessionContent[j].split(':')
                break
            else:
                j = j - 1

        beginContent = re.sub('\(.*?\)', '', beginContent)
        beginContent = re.split(r'[.,?!]', beginContent)
        beginContent = max(beginContent, key=len, default='').lower().strip()

        endContent = re.sub('\(.*?\)', '', endContent)
        endContent = re.split(r'[.,?!]', endContent)
        endContent = max(endContent, key=len, default='').lower().strip()

        beginTime = None
        endTime = None
        timeBlockNum1 = timeBlockNum2 = None
        for i in range(len(alternate)):
            # decide which is longer: script or subtitle?
            if len(alternate[i].content_en) <= len(beginContent):
                if alternate[i].content_en in beginContent:
                    beginTime = alternate[i].beginTime
                    timeBlockNum1 = alternate[i].timeBlockNum
                    break
            else:
                if beginContent in alternate[i].content_en:
                    beginTime = alternate[i].beginTime
                    timeBlockNum1 = alternate[i].timeBlockNum
                    break

        for i in range(len(alternate)):
            if len(alternate[i].content_en) <= len(endContent):
                if alternate[i].content_en in endContent:
                    endTime = alternate[i].endTime
                    timeBlockNum2 = alternate[i].timeBlockNum
                    break
            else:
                if endContent in alternate[i].content_en:
                    endTime = alternate[i].endTime
                    timeBlockNum2 = alternate[i].timeBlockNum
                    break
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
        if episode.sessionList[i].endTimeBlockNum is None and episode.sessionList[i+1].beginTimeBlockNum:
            episode.sessionList[i].sessionEndTime = subtitle.timeBlockList[episode.sessionList[i+1].beginTimeBlockNum-1].beginTime

def setTime(episode,subtitle):
    dic = {}
    for s in subtitle.timeBlockList:
        temp = {s.beginTime: s.timeBlockNum}
        dic.update(temp)

    episode.sessionList[7].sessionBeginTime = '00:17:38,960 '
    episode.sessionList[7].beginTimeBlockNum = dic[episode.sessionList[7].sessionBeginTime]
    episode.sessionList[46].sessionBeginTime = '00:18:11,170 '
    episode.sessionList[46].beginTimeBlockNum = dic[episode.sessionList[46].sessionBeginTime]
    episode.sessionList[54].sessionBeginTime = '00:15:39,540 '
    episode.sessionList[54].beginTimeBlockNum = dic[episode.sessionList[54].sessionBeginTime]
    episode.sessionList[62].sessionBeginTime = '00:20:15,120 '
    episode.sessionList[62].beginTimeBlockNum = dic[episode.sessionList[62].sessionBeginTime]
    episode.sessionList[71].sessionBeginTime = '00:04:37,480 '
    episode.sessionList[71].beginTimeBlockNum = dic[episode.sessionList[71].sessionBeginTime]
    episode.sessionList[77].sessionBeginTime = '00:03:06,730 '
    episode.sessionList[77].beginTimeBlockNum = dic[episode.sessionList[77].sessionBeginTime]
    episode.sessionList[114].sessionBeginTime = '00:18:59,960 '
    episode.sessionList[114].beginTimeBlockNum = dic[episode.sessionList[114].sessionBeginTime]
    episode.sessionList[160].sessionBeginTime = '00:19:19,920 '
    episode.sessionList[160].beginTimeBlockNum = dic[episode.sessionList[160].sessionBeginTime]

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
    print(noBegin,noEnd)
    """for begin in noBegin:
        print(episode.sessionList[begin].sessionContent)"""
if __name__ == '__main__':
    args = parse_config()
    main(args)