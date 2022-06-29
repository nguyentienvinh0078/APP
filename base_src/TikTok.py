import os, re, time, sys, json, requests


class TikTok():
    def __init__(self):
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36 Edg/87.0.664.66'
        }

        self.rootDir = self.getRootDir()
        self.tiktokFolder = "TikTok"
        self.savePathFolder = os.path.join(self.rootDir, self.tiktokFolder)
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

    def getTiktokUrlInput(self, maxAgain=3):
        for againNumber in range(maxAgain):
            print(">> Enter TikTok Url, Enter \"Close\" to Exit!")
            print('-' * 120)
            tiktokUrl = re.sub("[^\x00-\xff]", '', input('>> TikTok Url: ')).replace(' ', '')
            os.system("cls")
            print('-' * 120)
            tiktokUrlInputSuccess = False
            if  "tiktok.com" in tiktokUrl:
                tiktokUrlInputSuccess = True
                print('>> Successfully entered the TikTok Url!')
                print('-' * 120)
                break
            elif tiktokUrl.title() == "Close":
                print('======== Exit! ========')
                print('-' * 120)
                break
            else:
                os.system("cls")
                print('-' * 120)
                print(f'>> Error, Please check Tiktok url!')
                print('-' * 120)
        return tiktokUrl, tiktokUrlInputSuccess

    def createFolder(self, folderPath):
        try: 
            if not os.path.exists(folderPath):
                os.makedirs(folderPath)
        except Exception as bug:
            print(f"CreateFolder Function: {bug}")
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
                print(f"requestsDeal Function: {bug}")
                continue

    def tikTokUrlCheck(self, tiktokUrl):
        urlInfo = {}

        if 'www.tiktok.com' in tiktokUrl:
            realTikTokUrl = tiktokUrl.split('?')[0]
        elif 'vt.tiktok.com' in tiktokUrl:
            response = self.requestDeal(tiktokUrl)
            realTikTokUrl = response.url.split('?')[0]
        
        if '/video/' in realTikTokUrl:
            urlInfo = {
                "typeUrl": self.isVideo,
                "secUid": re.findall('\@(.*)' + '/video/', realTikTokUrl)[0],
                "videoId": re.findall('/video/(\d+)', realTikTokUrl)[0]
            }
        else:
            urlInfo = {
                "typeUrl": self.isUserPage,
                "secUid": re.findall('\@(.*)', realTikTokUrl)[0],
                "videoId": ""
            }
        return urlInfo

    def getUserId(self, nickname):
        userIdApi = 'https://t.tiktok.com/node/share/user/@{}?aid=1988'.format(nickname)
        response = self.requestDeal(userIdApi)
        if response.status_code == 200:
            userData = response.json()
            try:
                return str(userData["userInfo"]["user"]["id"])
            except Exception as bug:
                return str(userData['seoProps']['pageId'])

    def getNicknameAndUrlNoWatermark(self, videoId):
        try:
            videoApi = f'https://api.tiktokv.com/aweme/v1/multi/aweme/detail/?aweme_ids=%5B{videoId}%5D'
            js = json.loads(self.requestDeal(videoApi).text)
            nickname = str(js["aweme_details"][0]['author']["unique_id"]) #tiktok
            videoUrlNoWatermark = str(js["aweme_details"][0]["video"]["play_addr"]["url_list"][0]) #tiktok
        except Exception as bug:
            print(f"Nickname, urlNowatermark Functions: {bug}")
            pass
        
        return {
            'nickname': nickname,
            'url': videoUrlNoWatermark,  
        }

    def getVideoUrl(self, nickname, videoId):
        return f'https://www.tiktok.com/@{nickname}/video/{videoId}'

    def getVideoData(self, tiktokUrl, savePathFolder, jsonOutput=False):
        videoDataInfo = []
        urlInfo = self.tikTokUrlCheck(tiktokUrl) # return => typeUrl, nickname, videoId
        typeUrl = urlInfo['typeUrl']
        index = 0
        if typeUrl == self.isUserPage:
            nickname = urlInfo['secUid']
            userId = self.getUserId(nickname)

            minCursor = '0'; maxCursor = '0'; done = False
            while not done:
                nextDataApi = f'https://www.tiktok.com/share/item/list?id={userId}&type=1&count=100&maxCursor={maxCursor}&minCursor={minCursor}'
                response = self.requestDeal(nextDataApi)
                if response.status_code == 200:
                    js = response.json()
                    itemListData = js['body']['itemListData']
                    maxCursor = js['body']['maxCursor']
                    done = not js['body']['hasMore']

                    for videoItem in itemListData:
                        videoId = str(videoItem['itemInfos']['id'])
                        nickname = nickname,
                        try:
                            videoApi = f'https://api.tiktokv.com/aweme/v1/multi/aweme/detail/?aweme_ids=%5B{videoId}%5D'
                            js = json.loads(self.requestDeal(videoApi).text)
                            nickname = str(js["aweme_details"][0]['author']["unique_id"]) #tiktok
                            videoUrlNoWatermark = str(js["aweme_details"][0]["video"]["play_addr"]["url_list"][0]) #tiktok
                        except Exception as bug:
                            print(f"Nickname, urlNowatermark: {bug}")
                            pass
                        videoUrl = f'https://www.tiktok.com/@{nickname}/video/{videoId}',
                        videoUrlNoWatermark = videoUrlNoWatermark
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
            try:
                videoApi = f'https://api.tiktokv.com/aweme/v1/multi/aweme/detail/?aweme_ids=%5B{videoId}%5D'
                js = json.loads(self.requestDeal(videoApi).text)
                nickname = str(js["aweme_details"][0]['author']["unique_id"]) #tiktok
                videoUrlNoWatermark = str(js["aweme_details"][0]["video"]["play_addr"]["url_list"][0]) #tiktok
            except Exception as bug:
                print(f"Nickname, urlNowatermark: {bug}")
                pass
            videoUrl = f'https://www.tiktok.com/@{nickname}/video/{videoId}',
            videoUrlNoWatermark = videoUrlNoWatermark
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
            
            try:
                if filename in saveFolderListDir:
                    print(f'>> {index+1:2>} / {dataLength}, file [ {filename} ] was Exists, Download skip! ', end = "")
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
                    print(f'>> Total: {index+1:2>} / {dataLength}')
                    print(f'>> Downloading... [ {filename} ] --')
                    startDownloadTime = time.time()
                    size = 0; chunkSize = 1024
                    video = self.requestDeal(videoUrlNoWatermark)
                    contentSize = int(video.headers['content-length'])
                    MBSize = round(contentSize / chunkSize / chunkSize, 2)

                    if video.status_code == 200:
                        with open(file=filePath, mode='wb') as file:
                            for data in video.iter_content(chunk_size=chunkSize):
                                file.write(data)
                                size = size + len(data)  
                                print('\r' + '>>%s%.2f%%' % ('>'*int(size*40/contentSize), float(size/contentSize*100)), end=' ')
                    endDownloadTime = time.time()
                    totalDownloadTime = endDownloadTime - startDownloadTime
                    print(f'\n>> Download time: {totalDownloadTime:.2f}s -- Size: {MBSize:.2f}MB')
                    print('-' * 120)
                    break
                except Exception as bug:
                    print(f"Download: {bug}")
                    continue

    def main(self):
        self.urlListTest = [
            'https://www.tiktok.com/@yenkim07022004__',
            'https://www.tiktok.com/@yenkim07022004__?is_from_webapp=1&sender_device=pc',
            'https://vt.tiktok.com/ZSdgm4UNs/',

            'https://www.tiktok.com/@yenkim07022004__/video/7104196143575239962?is_from_webapp=1&sender_device=pc&web_id=7077083055764915713',
            'https://www.tiktok.com/@yenkim07022004__/video/7104489383570509083?is_copy_url=1&is_from_webapp=v1',
            'https://vt.tiktok.com/ZSdgmCNn2/?k=1',
        ]

        while True:
            tiktokUrl, tiktokUrlInputSuccess = self.getTiktokUrlInput()
            if tiktokUrlInputSuccess:
                print('>> Getting Data Please Wait A Minute!')
                print('-' * 120)
                videoDataInfo = self.getVideoData(tiktokUrl)
                self.download(videoDataInfo)
            else: break
            
def main():
    try:
        tikTok = TikTok()
        tikTok.main()
    except Exception as bug:
        print(f"Main: {bug}")
        os.system('pause')

if __name__ == '__main__':
    main()