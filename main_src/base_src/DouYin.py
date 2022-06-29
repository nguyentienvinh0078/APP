import os, re, time, sys, json, requests


class DouYin():
    def __init__(self):
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36 Edg/87.0.664.66'
        }

        self.rootDir = self.getRootDir()
        self.douyinFolder = "DouYin"
        self.savePathFolder = os.path.join(self.rootDir, self.douyinFolder)
        self.isUserPage = "Multiple Video"
        self.isVideo = "Video"

    def getRootDir(selef):
        rootPath = ''
        if getattr(sys, 'frozen', False):
            rootPath = os.path.dirname(sys.executable)
        else: 
            try:
                rootPath = os.path.dirname(os.path.realpath(__file__))
            except NameError:
                rootPath = os.getcwd()
        return rootPath 

    def getdouyinUrlInput(self, maxAgain=3):
        for againNumber in range(maxAgain):
            print(">> Enter DouYin Url, Enter \"Close\" to Exit!")
            print('-' * 120)
            douyinUrl = re.sub("[^\x00-\xff]", '', input('>> DouYin Url: ')).replace(' ', '')
            os.system("cls")
            print('-' * 120)
            douyinUrlInputSuccess = False
            if  "douyin.com" in douyinUrl:
                douyinUrlInputSuccess = True
                print('>> Successfully entered the DouYin Url!')
                print('-' * 120)
                break
            elif douyinUrl.title() == "Close":
                print('======== Exit! ========')
                print('-' * 120)
                break
            else:
                os.system("cls")
                print('-' * 120)
                print(f'>> Error, Please check DouYin Url!')
                print('-' * 120)
        return douyinUrl, douyinUrlInputSuccess

    def createFolder(self, folderPath):
        try: 
            if not os.path.exists(folderPath):
                os.makedirs(folderPath)
        except Exception as bug:
            print(f"CreateFolder Funtion: {bug}")
            return

    def jsonFileWrite(self, jsonData, jsonPath):
        with open(jsonPath, mode='w', encoding='utf-8') as jsonFile:
            json.dump(jsonData, jsonFile, indent=4, separators=(',',': '))
    
    def jsonFileRead(self, jsonData, jsonPath):
        resultData = []
        with open(jsonPath, mode='r', encoding='utf-8') as jsonData:
            resultData = json.load(jsonData)
        return resultData

    def requestDeal(self, url, maxAgain=3):
        for againNumber in range(maxAgain):
            try:
                return requests.get(url=url, headers=self.headers, timeout=25)
            except Exception as bug:
                print(f"REquestDeal Function: {bug}")
                continue

    def douyinUrlCheck(self, douyinUrl):
        urlInfo = {}
        
        if 'www.douyin.com' in douyinUrl:
            realDouyinUrl = douyinUrl.split('?')[0]
        elif 'v.douyin.com' in douyinUrl:
            response = self.requestDeal(douyinUrl)
            realDouyinUrl = response.url.split('?')[0]
        
        if '/user/' in realDouyinUrl:
            if 'modal_id' not in douyinUrl:
                urlInfo = {
                    "typeUrl": self.isUserPage,
                    "secUid": re.findall('/user/(.*)', realDouyinUrl)[0],
                    "videoId": "",
                }
            else:
                urlInfo = {
                    "typeUrl": self.isVideo,
                    "secUid": "",
                    "videoId": re.findall('modal_id=(\d+)', douyinUrl)[0],
                }
                
        elif '/video/' in realDouyinUrl:
            urlInfo = {
                "typeUrl": self.isVideo,
                "secUid": "",
                "videoId": re.findall('/video/(\d+)', realDouyinUrl)[0],
            }
        return urlInfo

    def getNicknameAndUrlNoWatermark(self, videoId):
        try:
            videoApi = 'https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids={}'.format(videoId)
            js = json.loads(self.requestDeal(videoApi).text)
            nickname = str(js['item_list'][0]['author']['nickname']) #douyin
            videoUrlNoWatermark = str(js['item_list'][0]['video']['play_addr']['url_list'][0]).replace('playwm', 'play') #douyin
        except Exception as bug:
            print(f"Function Nickname, urlNowatermark: {bug}")
            pass
        
        return {
            'nickname': nickname,
            'url': videoUrlNoWatermark
        }

    def getVideoUrl(self, videoId):
        return f'https://www.douyin.com/video/{videoId}'

    def getVideoData(self, douyinUrl, savePathFolder, jsonOutput=True):
        videoDataInfo = []
        urlInfo = self.douyinUrlCheck(douyinUrl) # return => typeUrl, nickname, videoId
        typeUrl = urlInfo['typeUrl']
        index = 0
        if typeUrl == self.isUserPage:
            secUid = urlInfo['secUid']
            minCursor = '0'; maxCursor = '0'; done = False
            while not done:
                nextDataApi = f'https://www.iesdouyin.com/web/api/v2/aweme/post/?sec_uid={secUid}&count=30&max_cursor={maxCursor}&min_cursor={minCursor}&aid=1128&_signature=PDHVOQAAXMfFyj02QEpGaDwx1S&dytk='
                response = self.requestDeal(nextDataApi)
                if response.status_code == 200:
                    js = response.json()
                    itemListData = js['aweme_list']
                    maxCursor = str(js['max_cursor'])
                    done = not js['has_more']

                    for videoItem in itemListData:
                        videoId = str(videoItem['aweme_id'])
                        videoUrl = f'https://www.douyin.com/video/{videoId}'
                        try:
                            videoApi = 'https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids={}'.format(videoId)
                            js = json.loads(self.requestDeal(videoApi).text)
                            nickname = str(js['item_list'][0]['author']['nickname']) #douyin
                            videoUrlNoWatermark = str(js['item_list'][0]['video']['play_addr']['url_list'][0]).replace('playwm', 'play') #douyin
                        except Exception as bug:
                            print(f"Nickname, urlNowatermark: {bug}")
                            pass
                        saveFolder = os.path.join(savePathFolder, typeUrl, nickname)
                        videoDataInfo.append({
                            'videoNumber': str(index),
                            'videoId': videoId,
                            'nickname': nickname,
                            'videoUrl': videoUrl,
                            'videoUrlNoWatermark': videoUrlNoWatermark,
                            'saveFolder': saveFolder
                        })
                        print(f'>> Index: {index+1:>2} -- Nickname: {nickname} -- ID: {videoId}')
                        print('-' * 120)
                        index = index + 1

        elif typeUrl == self.isVideo:
            videoId = urlInfo['videoId']
            videoUrl = f'https://www.douyin.com/video/{videoId}'
            try:
                videoApi = 'https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids={}'.format(videoId)
                js = json.loads(self.requestDeal(videoApi).text)
                nickname = str(js['item_list'][0]['author']['nickname']) #douyin
                videoUrlNoWatermark = str(js['item_list'][0]['video']['play_addr']['url_list'][0]).replace('playwm', 'play') #douyin
            except Exception as bug:
                print(f"Nickname, urlNowatermark: {bug}")
                pass
            saveFolder = os.path.join(savePathFolder, typeUrl, nickname)
            videoDataInfo.append({
                'videoNumber': str(index),
                'videoId': videoId,
                'nickname': nickname,
                'videoUrl': videoUrl,
                'videoUrlNoWatermark': videoUrlNoWatermark,
                'saveFolder': saveFolder
            })
            print(f'>> Index: {index+1:>2} -- Nickname: {nickname} -- ID: {videoId}')
            print('-' * 120)
            index = index + 1
        
        if jsonOutput:
            saveFolder = videoDataInfo[0]['saveFolder']
            if len(videoDataInfo) > 1:
                jsonFilePath = f'{saveFolder}_backup.json'
                self.createFolder(saveFolder)
                self.jsonFileWrite(videoDataInfo, jsonFilePath)

        return videoDataInfo
    
    def download(self, videoDataInfo):
        dataLength = len(videoDataInfo)
        for index in range(dataLength):
            saveFolder = videoDataInfo[index]['saveFolder']
            videoId = videoDataInfo[index]['videoId']
            videoUrlNoWatermark = videoDataInfo[index]['videoUrlNoWatermark']

            filename = f'{videoId}.mp4'
            filePath = f'{saveFolder}\{filename}'
            
            self.createFolder(saveFolder)
            saveFolderListDir = os.listdir(saveFolder)
            
            videoIndex = index + 1
            try:
                if filename in saveFolderListDir:
                    print(f'>> {videoIndex:2>} / {dataLength}, file [ {filename} ] was Exists, Download skip! ', end = "")
                    for i in range(15):
                        print(">", end='', flush=True)
                        time.sleep(0.01)
                    print('\r')
                    print('-' * 120)
                    continue    
            except Exception as bug:
                print(f"Check file Exists: {bug}")
                pass
            retryDownloadMax = 3
            for againNumber in range(retryDownloadMax):
                try:
                    print(f'>> Total: {videoIndex:>2} / {dataLength}')
                    print(f'>> Downloading... [ {filename} ] --')
                    startDownloadTime = time.time()
                    size = 0; chunkSize = 1024
                    video = self.requestDeal(videoUrlNoWatermark)
                    contentSize = int(video.headers['content-length'])
                    MB_size = round(contentSize / chunkSize / 1024, 2)

                    if video.status_code == 200:
                        with open(file=filePath, mode='wb') as file:
                            for data in video.iter_content(chunk_size=chunkSize):
                                file.write(data)
                                size = size + len(data)
                                print('\r' + '>>%s%.2f%%' % ('>'*int(size*40/contentSize), float(size/contentSize*100)), end=' ')
                    endDownloadTime = time.time()
                    totalDownloadTime = endDownloadTime - startDownloadTime
                    print(f'\n>> Download time: {totalDownloadTime:.2f}s -- Size: {MB_size:.2f}MB')
                    print('-' * 120)
                    break
                except Exception as bug:
                    print(f"Download: {bug}")
                    continue

    def main(self):
        self.urlListTest = [
            'https://www.douyin.com/user/MS4wLjABAAAAN_oREEJGh0mT9IK1jLnsJQLdy_kFZ51w2VSH0EyafJdh_vcOXR5K8eFMLRt79mMh',
            # 'https://v.douyin.com/JcjJ5Tq/',
            
            'https://www.douyin.com/user/MS4wLjABAAAAt7VyKvSkkHz_WufLbS8dKIR5tQwCprWUJATHh49BTRU?modal_id=7015104885855112451',
            'https://www.douyin.com/video/7102734573259263271',
            'https://v.douyin.com/FKcep5Y/'
        ]

        while True:
            douyinUrl, douyinUrlInputSuccess = self.getdouyinUrlInput()
            if douyinUrlInputSuccess:
                print('>> Getting Data Please Wait A Minute!')
                print('-' * 120)
                videoDataInfo = self.getVideoData(douyinUrl, self.savePathFolder)
                self.download(videoDataInfo)
            else: break

def main():
    try:
        douyin = DouYin()
        douyin.main()
    except Exception as bug:
        print(f"Main: {bug}")

        os.system('pause')

if __name__ == '__main__':
    main() 