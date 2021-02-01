import Cryptodome,random,base64,requests,os,json
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad
class Encryption(object):
    def __init__(self):
        self.char = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        self.iv = '0102030405060708' #偏移量
        self.key1 = "010001"
        self.key2 = "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7"
        self.key3 = "0CoJUm6Qyw8W8jud"

    def RandomStr(self,numLen):#生成numLen位随机字符串
        char = self.char
        tempStr = ''
        for i in range(numLen):
            index = random.randint(1,len(char))-1
            tempStr+=char[index]
        return tempStr

    def AESEncrypt(self,target,key,iv):
        target = pad(data_to_pad=target.encode(), block_size=AES.block_size)
        key = key.encode()
        iv = iv.encode()
        aes = AES.new(key=key, mode=AES.MODE_CBC, iv=iv)
        cipher_text = aes.encrypt(plaintext=target)
        # 字节串转为字符串
        cipher_texts = base64.b64encode(cipher_text).decode()
        return cipher_texts

    def RSAEncrypt(self,i,e,n):
        num = pow(int(i[::-1].encode().hex(), 16), int(e, 16), int(n, 16))
        result = format(num, 'x')
        return result
        
    def NEEncrypt(self,target):

        key1 = self.key1
        key2 = self.key2
        key3 = self.key3
        iv = self.iv
        h = {}
        i = self.RandomStr(16)
        h['encText'] = self.AESEncrypt(target,key3,iv)
        h['encText'] = self.AESEncrypt(h['encText'],i,iv)
        h['encSecKey'] = self.RSAEncrypt(i,key1,key2)
        return h

class Netease(object):
    def __init__(self):
        self.encryption = Encryption()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2'
            }
        self.cookies = {
            #'MUSIC_U':'9de0b492647e4661a3ee28436a9b8355dfe0b23d1549bfa62445fadb65fd6ac01e857ebc9b97e72289fb087bccb04b4954b28db031a9be2dbf122d59fa1ed6a2',
            #'__csrf':'176417248ae75057cf455e895232ea21'
            }
        self.session = requests.Session() #启动session
    
    def GetMusicUrl(self,musicId,level='standard'):
        url = 'https://music.163.com/weapi/song/enhance/player/url/v1?csrf_token='
        headers = self.headers
        cookies = self.cookies
        keyDict = {
            'ids':'['+str(musicId)+']',
            'level':level,
            'encodeType':'aac',
            'csrf_token':''
        }
        key = json.dumps(keyDict)
        data = self.encryption.NEEncrypt(key)
        dataDict = {
            'params':data['encText'],
            'encSecKey':data['encSecKey']
            }
        res = self.session.post(url,headers=headers,data=dataDict,cookies=cookies)
        res.raise_for_status()
        res.encoding = 'utf-8'
        data = res.json()
        try:
            musicUrl = data['data'][0]['url']
        except:
            print(res.text)
            musicUrl = False
        return musicUrl

    def GetComments(self,musicId,pageNo=1):
        url = 'https://music.163.com/weapi/comment/resource/comments/get?csrf_token='
        headers = self.headers
        cookies = self.cookies        
        keyDict = {
            'rid':'R_SO_4_'+str(musicId),
            'threadId':'R_SO_4_'+str(musicId),
            'pageNo':str(pageNo),
            'pageSize':'20',
            'orderType':'1',
            'offset':'0',
            'cursor':'-1',
            'csrf_token':''
        }
        key = json.dumps(keyDict)
        data = self.encryption.NEEncrypt(key)
        dataDict = {
            'params':data['encText'],
            'encSecKey':data['encSecKey']
            }
        res = self.session.post(url,headers=headers,data=dataDict,cookies=cookies)
        res.raise_for_status()
        res.encoding = 'utf-8'
        data = res.json()
        try:
            commentList = data
        except:
            print(res.text)
            commentList = False
        return commentList

    def NESearch(self,keyword):
        url = 'https://music.163.com/weapi/cloudsearch/get/web?csrf_token='
        headers = self.headers
        cookies = self.cookies        
        keyDict = {
            'hlpretag':'<span class=\"s-fc7\">',
            'hlposttag':'</span>',
            's':str(keyword),
            'type':'1',
            'total':'true',
            'offset':'0',
            'limit':'90',
            'csrf_token':''
        }
        key = json.dumps(keyDict)
        data = self.encryption.NEEncrypt(key)
        dataDict = {
            'params':data['encText'],
            'encSecKey':data['encSecKey']
            }
        res = self.session.post(url,headers=headers,data=dataDict,cookies=cookies)
        res.raise_for_status()
        res.encoding = 'utf-8'
        data = res.json()
        try:
            result = data['result']['songs']
        except:
            print(res.text)
            result = False
        return result

    def ShowPanel(self, data, limit=10):
        songs = data
        count = 0
        showList = []
        print('{:*^80}'.format('搜索结果如下'))
        print('{0:{5}<5}{1:{5}<20}{2:{5}<10}{3:{5}<10}{4:{5}<20}'.format('序号', '歌名', '歌手', '时长(s)', '专辑', chr(12288)))
        print('{:-^84}'.format('-'))
        for song in songs:
            songName = song['name']
            songId = song['id']
            songTime = song['dt'] // 1000
            songAlbumName = song['al']['name']
            songPicUrl = song['al']['picUrl']
            singer = song['ar'][0]['name']
            showList.append([songId, songName, singer])
            print('{0:{5}<5}{1:{5}<20}{2:{5}<10}{3:{5}<10}{4:{5}<20}'.format(count+1, songName, singer, songTime, songAlbumName, chr(12288)))
            count += 1
            if count == limit:
                break
        print('{:*^80}'.format('*'))
        while True:
            res = input("请输入要下载歌曲的序号(-1退出): ")
            try:
                choiceSong = showList[int(res)-1]
                break
            except:
                print('invalid input')
                choiceSong = False
                break
        return choiceSong

    def SaveMusic(self, musicUrl, dlInfo):
        filepath = './download'
        if not os.path.exists(filepath):
            os.mkdir(filepath)
        filename = dlInfo
        response = self.session.get(musicUrl, headers=self.headers)
        with open(os.path.join(filepath, filename) + '.mp3', 'wb') as f:
            f.write(response.content)
            print("下载完毕!")

if __name__ == '__main__':#执行层
    neObj = Netease()
    #neObj.GetComments(musicId='1501212275',pageNo=1)
    #url = neObj.GetMusicUrl(musicId='25727803')
    #neObj.SaveMusic(url,'一直在等')


def GetAllComments(neObj,musicId):
    data = neObj.GetComments(musicId=musicId,pageNo=1)
    totalNum = data['data']['totalCount']
    pageNoMax = totalNum/20
    for i in range(1,pageNoMax,1):
        pass



