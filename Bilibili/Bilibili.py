#!/usr/bin/env python3
# coding=utf-8
# author:sakuyo
#----------------------------------
import requests,time,csv
import pandas as pd
from enum import Enum


class BiliBili(object):

  def __init__(self):
    #初始化cookies
    self.cookies = {
      'SESSDATA':'4cd739a0%2C1614857849%2Cc6c2f*91'
    }
    #初始化请求头
    self.headers = {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
      'Accept': '*/*',
      'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2'
    }

  def login(self, username, password):#登录方法
    self.username = username
    self.password = password

  def saveToCSV(self, fileName, headers, contents):
    #titles = ['ShowTime','Mode','FontSize','FontColor','CommentTime','BarragePool','UserID','RowID','Content']
    titles = headers
    #data = self.barrageList
    data = contents
    #csv用utf-8-sig来保存
    with open(fileName+'.csv','a',newline='',encoding='utf-8-sig') as f:
      writer = csv.DictWriter(f,fieldnames=titles)
      writer.writeheader()
      writer.writerows(data)
      print('写入完成！')

class BiliBiliLive(BiliBili):

  def __init__(self,target):#初始化
    #BiliBili初始化
    BiliBili.__init__(self)
    self.target = target #target为直播间号
    
class BiliBiliAchive(BiliBili):

  def __init__(self,target):#初始化
    #BiliBili初始化
    BiliBili.__init__(self)
    self.target = target #target可为bvid，可为avid（aid）
    self.session = requests.Session() #启动弹幕读取session
    self.GetIdType()

  def GetIdType(self):#判断是bv号还是av号
    if self.target.isdigit():#通过是否全部为数字判断（待改进）
      self.GetAllId(aid = self.target)
    else:
      self.GetAllId(bvid = self.target)

  def GetAllId(self,bvid='',aid=''):#调用api获取bvid，avid和cid（cid即为oid）
    dataDict = {}
    url = 'https://api.bilibili.com/x/web-interface/view'
    
    if bvid != '': 
      dataDict['bvid'] = bvid
    
    if aid != '': 
      dataDict['aid'] = aid

    res = self.session.get(url,params=dataDict)
    res.raise_for_status()
    res.encoding = res.apparent_encoding
    data = res.json()
    #提取视频信息
    self.aid = data['data']['aid'] #av号 (pid)
    self.bvid = data['data']['bvid'] #bv号
    self.cid = data['data']['cid']
    self.title = data['data']['title'] #视频标题
    self.oid = self.cid #cid和oid相同
    self.pid = self.aid #pid和aid相同
    self.pubDate = data['data']['pubdate'] #视频发布日期

    print('aid/pid:{aid}, bvid:{bvid}, cid/oid:{cid}, title:{title}'.format(aid=self.aid, bvid=self.bvid, cid=self.cid, title=self.title))

class ReplyCatcher(BiliBiliAchive):
  
  def getReply(self):
    self.replyList = []
    url = 'https://api.bilibili.com/x/v2/reply'
    headers = self.headers
    #这里的oid不是cid是aid
    dataDict = {
      'type':1,
      'oid':self.aid,
      'jsonp':'jsonp',
      'pn':1
      }
    cookies = self.cookies
    res = self.session.get(url,headers=headers,params=dataDict,cookies=cookies)
    res.raise_for_status()
    res.encoding = 'utf-8'
    data = res.json()
    self.replyList = data['data']['replies']
    
class Danmaku(object):
  class FontSize(Enum):
    EXTREME_SMALL = 12
    SUPER_SMALL = 16
    SMALL = 18
    NORMAL = 25
    BIG = 36
    SUPER_BIG = 45
    EXTREME_BIG = 64

  class Mode(Enum):
    FLY = 1
    TOP = 5
    BOTTOM = 4
    REVERSE = 6

  def __init__(
    self,
    text: str,
    dm_time: float = 0.0,
    send_time: float = time.time(),
    crc32_id: str = None,
    color: str = 'ffffff',
    weight: int = -1,
    id_: int = -1,
    id_str: str = "",
    action: str = "",
    mode: Mode = Mode.FLY,
    font_size: FontSize = FontSize.NORMAL,
    is_sub: bool = False,
    pool: int = -1,
    attr: int = -1):
    """
    Args:
        text      (str)               : 弹幕文本。
        dm_time   (float, optional)   : 弹幕在视频中的位置，单位为秒。Defaults to 0.0.
        send_time (float, optional)   : 弹幕发送的时间。Defaults to time.time().
        crc32_id  (str, optional)     : 弹幕发送者 UID 经 CRC32 算法取摘要后的值。Defaults to None.
        color     (str, optional)     : 弹幕十六进制颜色。Defaults to "ffffff".
        weight    (int, optional)     : 弹幕在弹幕列表显示的权重。Defaults to -1.
        id_       (int, optional)     : 弹幕 ID。Defaults to -1.
        id_str    (str, optional)     : 弹幕字符串 ID。Defaults to "".
        action    (str, optional)     : 暂不清楚。Defaults to "".
        mode      (Mode, optional)    : 弹幕模式。Defaults to Mode.FLY.
        font_size (FontSize, optional): 弹幕字体大小。Defaults to FontSize.NORMAL.
        is_sub    (bool, optional)    : 是否为字幕弹幕。Defaults to False.
        pool      (int, optional)     : 暂不清楚。Defaults to -1.
        attr      (int, optional)     : 暂不清楚。 Defaults to -1.
    """
    self.text = text
    self.dm_time = dm_time
    self.send_time = send_time
    self.crc32_id = crc32_id
    self.color = color
    self.weight = weight
    self.id = id_
    self.id_str = id_str
    self.action = action
    self.mode = mode
    self.font_size = font_size
    self.is_sub = is_sub
    self.pool = pool
    self.attr = attr
    self.uid = None

  def __str__(self):
    ret = "uid: {uid}, 弹幕时间: {dm_time}, 弹幕文本: {text}".format(uid=self.uid, send_time=self.send_time, dm_time=self.dm_time, text=self.text)
    return ret

  def __len__(self):
    return len(self.text)

  def getDict(self):
    return {
      'text':self.text, 
      'dm_time':self.dm_time, 
      'send_time':self.send_time, 
      'crc32_id':self.crc32_id, 
      'color': self.color, 
      'weight':self.weight, 
      'id':self.id, 
      'action':self.action, 
      'mode':self.mode,
      'font_size':self.font_size,
      'uid':self.uid}

  def crack_uid(self):
    try:
      self.uid = int(crack_uid(self.crc32_id))
    except:
      self.uid = None
      return self.uid

class BarrageCatcher(BiliBiliAchive):
  
  def getAPI(self):
    url = 'https://api.bilibili.com/x/v2/dm/web/seg.so?type=1&oid={oid}&pid={pid}&segment_index={seg_index}'.format(oid=self.oid, pid=self.pid, seg_index=1)
    return url

  def getDm(self):
    raw = self.session.get(url=self.getAPI(), headers=self.headers).content
    return raw

  def decode(self, dm_raw):
    dm_list = []
    reader = BytesReader(dm_raw)
    while not reader.isEnd():
      reader.readInt() >> 3
      dm = Danmaku('')
      dm_pack = reader.readStr(bytes=True)
      dm_reader = BytesReader(dm_pack)
      while not dm_reader.isEnd():
        data_type = dm_reader.readInt() >> 3
        if data_type == 1:
          dm.id = dm_reader.readInt()
        elif data_type == 2:
          dm.dm_time = dm_reader.readInt() / 1000
        elif data_type == 3:
          dm.mode = dm_reader.readInt()
        elif data_type == 4:
          dm.font_size = dm_reader.readInt()
        elif data_type == 5:
          dm.color = hex(dm_reader.readInt())[2:]
        elif data_type == 6:
          dm.crc32_id = dm_reader.readStr()
          dm.crack_uid()
        elif data_type == 7:
          dm.text = dm_reader.readStr()
        elif data_type == 8:
          dm.send_time = dm_reader.readInt()
        elif data_type == 9:
          dm.weight = dm_reader.readInt()
        elif data_type == 10:
          dm.action = dm_reader.readInt()
        elif data_type == 11:
          dm.pool = dm_reader.readInt()
        elif data_type == 12:
          dm.id_str = dm_reader.readStr()
        elif data_type == 13:
          dm.attr = dm_reader.readInt()
        else:
          break
      dm_list.append(dm.getDict())
      print(dm.getDict())
    return dm_list

class BytesReader(object):
  def __init__(self, stream: bytes):
    self.stream = stream
    self.offset = 0

  def isEnd(self):
    self.offset >= len(self.stream)

  def readInt(self):
    value = 0
    position = 0
    shift = 0
    stream = self.stream[self.offset:]
    while True:
      if position >= len(stream):
          break
      byte = stream[position]
      value += (byte & 0b01111111) << shift
      if byte & 0b10000000 == 0:
          break
      position += 1
      shift += 7

    self.offset += position + 1  
    return value
    
  def readStr(self, encoding="utf8", bytes=False):
    str_len = self.readInt()
    data = self.stream[self.offset:self.offset + str_len]
    self.offset += str_len
    if bytes:
      pass
    else:
      data = data.decode(encoding=encoding, errors="ignore")
    return data

class UserCatcher(BiliBili):   
  def __init__(self):#初始化
    #BiliBili初始化
    BiliBili.__init__(self)
    self.session = requests.Session() #启动弹幕读取session

  def GetUserFollowerList(self,mid):#获取用户粉丝列表
    url = 'https://api.bilibili.com/x/relation/followers'
    headers = self.headers
    cookies = self.cookies
    dataDict = {
      'vmid':mid,
      'order':'desc',
      'jsonp':'jsonp'
      }
    res = self.session.get(url,headers=headers,params=dataDict,cookies=cookies)
    res.raise_for_status()
    res.encoding = res.apparent_encoding
    data = res.json()
    return data

  def GetUserFollowingList(self,mid):#获取用户关注列表
    url = 'https://api.bilibili.com/x/relation/followings'
    headers = self.headers
    cookies = self.cookies
    dataDict = {
      'vmid':mid,
      'order':'desc',
      'jsonp':'jsonp'
      }
    res = self.session.get(url,headers=headers,params=dataDict,cookies=cookies)
    res.raise_for_status()
    res.encoding = res.apparent_encoding
    data = res.json()
    return data

  def GetUserInfoByInfo(self,mid):#获取用户信息API ①
    #该API包含生日、等级、姓名、性别、硬币数、签名等
    url = 'https://api.bilibili.com/x/space/acc/info'
    headers = self.headers
    cookies = self.cookies
    dataDict = {
      'mid':mid,
      'jsonp':'jsonp'
      }
    res = self.session.get(url,headers=headers,params=dataDict,cookies=cookies)
    res.raise_for_status()
    res.encoding = res.apparent_encoding
    data = res.json()
    return data

  def GetUserInfoByStat(self,mid):#获取用户信息API ②
    #该API包含关注、粉丝数等
    url = 'https://api.bilibili.com/x/relation/stat'
    headers = self.headers
    cookies = self.cookies
    dataDict = {
      'vmid':mid,
      'jsonp':'jsonp'
      }
    res = self.session.get(url,headers=headers,params=dataDict,cookies=cookies)
    res.raise_for_status()
    res.encoding = res.apparent_encoding
    data = res.json()
    return data

  def GetUserInfoByUpStat(self,mid):#获取用户信息API ③
    #该API包含UP主视频播放量、文章阅读量、获赞数等
    url = 'https://api.bilibili.com/x/space/upstat'
    headers = self.headers
    cookies = self.cookies
    dataDict = {
      'mid':mid,
      'jsonp':'jsonp'
      }
    res = self.session.get(url,headers=headers,params=dataDict,cookies=cookies)
    res.raise_for_status()
    res.encoding = res.apparent_encoding
    data = res.json()
    return data

  def GetUserInfoByTagList(self,mid):#获取用户信息API ④
    #该API包含用户订阅标签
    url = 'https://api.bilibili.com/x/space/tag/sub/list'
    headers = self.headers
    cookies = self.cookies
    dataDict = {
      'vmid':mid,
      'jsonp':'jsonp'
      }
    res = self.session.get(url,headers=headers,params=dataDict,cookies=cookies)
    res.raise_for_status()
    res.encoding = res.apparent_encoding
    data = res.json()
    return data

  def GetUserInfo(self,mid):#提取用户信息（调用api）
    user = {}
    user['mid'] = mid
    #调用API
    infoData = self.GetUserInfoByInfo(mid)
    statData = self.GetUserInfoByStat(mid)
    upStatData = self.GetUserInfoByUpStat(mid)
    tagListData = self.GetUserInfoByTagList(mid)
    #提取用户信息
    user['birthday'] = infoData['data']['birthday']
    user['level'] = infoData['data']['level']
    user['name'] = infoData['data']['name']
    user['sex'] = infoData['data']['sex']
    user['coins'] = infoData['data']['coins']
    user['sign'] = infoData['data']['sign']
    user['official'] = infoData['data']['official']

    user['follower'] = statData['data']['follower']
    user['following'] = statData['data']['following']
    
    user['archive-view'] = upStatData['data']['archive']['view']
    user['article-view'] = upStatData['data']['article']['view']
    user['likes'] = upStatData['data']['likes']

    user['tag-list'] = tagListData['data']['tags']
    return user

"""
此方法引用自https://github.com/MoyuScript/bilibili-api/blob/a40d743089b70a0d0c73207690eb33a38cf28804/bilibili_api/utils/utils.py
"""
def crack_uid(crc32: str):
    __CRCPOLYNOMIAL = 0xEDB88320
    __crctable = [None] * 256
    __index = [None] * 4

    def __create_table():
        for i in range(256):
            crcreg = i
            for j in range(8):
                if (crcreg & 1) != 0:
                    crcreg = __CRCPOLYNOMIAL ^ (crcreg >> 1)
                else:
                    crcreg >>= 1
            __crctable[i] = crcreg

    __create_table()

    def __crc32(input_):
        if type(input_) != str:
            input_ = str(input_)
        crcstart = 0xFFFFFFFF
        len_ = len(input_)
        for i in range(len_):
            index = (crcstart ^ ord(input_[i])) & 0xFF
            crcstart = (crcstart >> 8) ^ __crctable[index]
        return crcstart

    def __crc32lastindex(input_):
        if type(input_) != str:
            input_ = str(input_)
        crcstart = 0xFFFFFFFF
        len_ = len(input_)
        index = None
        for i in range(len_):
            index = (crcstart ^ ord(input_[i])) & 0xFF
            crcstart = (crcstart >> 8) ^ __crctable[index]
        return index

    def __getcrcindex(t):
        for i in range(256):
            if __crctable[i] >> 24 == t:
                return i
        return -1

    def __deepCheck(i, index):
        tc = 0x00
        str_ = ""
        hash_ = __crc32(i)
        tc = hash_ & 0xFF ^ index[2]
        if not (57 >= tc >= 48):
            return [0]
        str_ += str(tc - 48)
        hash_ = __crctable[index[2]] ^ (hash_ >> 8)

        tc = hash_ & 0xFF ^ index[1]
        if not (57 >= tc >= 48):
            return [0]
        str_ += str(tc - 48)
        hash_ = __crctable[index[1]] ^ (hash_ >> 8)

        tc = hash_ & 0xFF ^ index[0]
        if not (57 >= tc >= 48):
            return [0]
        str_ += str(tc - 48)
        hash_ = __crctable[index[0]] ^ (hash_ >> 8)

        return [1, str_]

    ht = int(crc32, 16) ^ 0xFFFFFFFF
    i = 3
    while i >= 0:
        __index[3-i] = __getcrcindex(ht >> (i*8))
        # pylint: disable=invalid-sequence-index
        snum = __crctable[__index[3-i]]
        ht ^= snum >> ((3-i)*8)
        i -= 1
    for i in range(10000000):
        lastindex = __crc32lastindex(i)
        if lastindex == __index[3]:
            deepCheckData = __deepCheck(i, __index)
            if deepCheckData[0]:
                break
    if i == 10000000:
        return -1
    return str(i) + deepCheckData[1]

if __name__ == '__main__':#执行层
  targetBv = 'BV16r4y1D74C'
  bcObj = BarrageCatcher(target = targetBv)
  dm_list = bcObj.decode(bcObj.getDm())
  pd.DataFrame(dm_list).to_csv(bcObj.title)