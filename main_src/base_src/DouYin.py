import os, re, time, sys, json, requests
from subprocess import REALTIME_PRIORITY_CLASS


class DouYin():
    def __init__(self):
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36 Edg/87.0.664.66'
        }

        self.root_dir = self.get_root_dir()
        self.parent_folder = 'DouYin'
        self.save_path = os.path.join(self.root_dir, self.parent_folder)
        self.multiple_video_type = 'Multiple Video'
        self.video_type = 'Video'

    def download(self, video_data_info):
        data_length = len(video_data_info)
        for index in range(data_length):
            video_id = video_data_info[index]['video_id']
            url_nowatermark = video_data_info[index]['url_nowatermark']
            save_folder = video_data_info[index]['save_folder']

            filename = f'{video_id}.mp4'
            filePath = f'{save_folder}\{filename}'
            
            self.create_folder(save_folder)
            save_folder_list_dir = os.listdir(save_folder)
            
            video_index = index + 1
            try:
                if filename in save_folder_list_dir:
                    print(f'>> {video_index:2>} / {data_length}, file [ {filename} ] was Exists, Download skip! ', end = "")
                    for i in range(15):
                        print(">", end='', flush=True)
                        time.sleep(0.01)
                    print('\r')
                    print('-' * 120)
                    continue    
            except Exception as bug:
                print(f"Check file Exists: {bug}")
                pass

            retry_download_max = 3
            for again_number in range(retry_download_max):
                try:
                    print(f'>> Total: {video_index:>2} / {data_length}')
                    print(f'>> Downloading... [ {filename} ] --')
                    start_download_time = time.time()
                    size = 0; chunkSize = 1024
                    video = self.requests_deal(url_nowatermark)
                    contentSize = int(video.headers['content-length'])
                    MB_size = round(contentSize / chunkSize / 1024, 2)

                    if video.status_code == 200:
                        with open(file=filePath, mode='wb') as file:
                            for data in video.iter_content(chunk_size=chunkSize):
                                file.write(data)
                                size = size + len(data)
                                print('\r' + '>>%s%.2f%%' % ('>'*int(size*40/contentSize), float(size/contentSize*100)), end=' ')
                    end_download_time = time.time()
                    total_download_time = end_download_time - start_download_time
                    print(f'\n>> Download time: {total_download_time:.2f}s -- Size: {MB_size:.2f}MB')
                    print('-' * 120)
                    break
                except Exception as bug:
                    print(f"Download: {bug}")
                    continue

    def get_video_data(self, douyin_url, json_output=False):
        video_data_info = []
        real_douyin_url = self.get_real_douyin_url(douyin_url)
        url_type = self.get_url_type(real_douyin_url)
        index = 0
        if url_type == self.multiple_video_type:
            sec_uid = self.get_sec_uid(real_douyin_url)
            min_cursor = '0'; max_cursor = '0'; done = False
            while not done:
                next_data_api = f'https://www.iesdouyin.com/web/api/v2/aweme/post/?sec_uid={sec_uid}&count=30&max_cursor={max_cursor}&min_cursor={min_cursor}&aid=1128&_signature=PDHVOQAAXMfFyj02QEpGaDwx1S&dytk='
                response = self.requests_deal(next_data_api)
                if response.status_code == 200:
                    js = response.json()
                    item_list_data = js['aweme_list']
                    max_cursor = str(js['max_cursor'])
                    done = not js['has_more']

                    for video_item in item_list_data:
                        video_id = str(video_item['aweme_id'])
                        try:
                            video_api = 'https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids={}'.format(video_id)
                            js = json.loads(self.requests_deal(video_api).text)
                            nickname = str(js['item_list'][0]['author']['nickname']) #douyin
                            url_nowatermark = str(js['item_list'][0]['video']['play_addr']['url_list'][0]).replace('playwm', 'play') #douyin
                        except Exception as bug:
                            print(f"Nickname, urlNowatermark: {bug}")
                            pass
                        video_data_info.append({
                            'video_index': str(index),
                            'video_id': video_id,
                            'nickname': nickname,
                            'video_url': f'https://www.douyin.com/video/{video_id}',
                            'url_nowatermark': url_nowatermark,
                            'save_folder': os.path.join(self.save_path, url_type, nickname),
                        })
                        print(f'>> Index: {index+1:>2} -- Nickname: {nickname} -- ID: {video_id}')
                        print('-' * 120)
                        index = index + 1

        elif url_type == self.video_type:
            video_id = self.get_video_id(real_douyin_url)
            try:
                video_api = 'https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids={}'.format(video_id)
                js = json.loads(self.requests_deal(video_api).text)
                nickname = str(js['item_list'][0]['author']['nickname']) #douyin
                url_nowatermark = str(js['item_list'][0]['video']['play_addr']['url_list'][0]).replace('playwm', 'play') #douyin
            except Exception as bug:
                print(f"Nickname, urlNowatermark: {bug}")
                pass
            video_data_info.append({
                'video_index': str(index),
                'video_id': video_id,
                'nickname': nickname,
                'video_url': f'https://www.douyin.com/video/{video_id}',
                'url_nowatermark': url_nowatermark,
                'save_folder': os.path.join(self.save_path, url_type, nickname),
            })
            print(f'>> Index: {index+1:>2} -- Nickname: {nickname} -- ID: {video_id}')
            print('-' * 120)
            index = index + 1
        
        if json_output:
            save_folder = video_data_info[0]['save_folder']
            if len(video_data_info) > 1:
                jsonFilePath = f'{save_folder}_backup.json'
                self.createFolder(save_folder)
                self.jsonFileWrite(video_data_info, jsonFilePath)

        return video_data_info

    def get_url_type(self, real_douyin_url):
        if '/video/' in real_douyin_url:
            return self.video_type
        return self.multiple_video_type

    def get_sec_uid(self, real_douyin_url):
        if '/video/' in real_douyin_url:
            return ""
        return re.findall('/user/(.*)', real_douyin_url)[0]

    def get_video_id(self, real_douyin_url):
        if '/video/' in real_douyin_url:
            return re.findall('/video/(\d+)', real_douyin_url)[0]
        return ""

    def get_real_douyin_url(self, douyin_url):
        real_douyin_url = ''
        if 'modal_id' in douyin_url:
            try:
                video_id = douyin_url.split('?')[1].split('=')[1]
            except:
                video_id = douyin_url[-19:]
            real_douyin_url = f'https://www.douyin.com/video/{video_id}'
        elif 'www.douyin.com' in douyin_url:
            real_douyin_url = douyin_url.split('?')[0]
        elif 'v.douyin.com' in douyin_url:
            response = self.requests_deal(douyin_url)
            real_douyin_url = response.url.split('?')[0]
        return real_douyin_url

    def requests_deal(self, url, max_again=3):
        for again_number in range(max_again):
            try:
                return requests.get(url=url, headers=self.headers, timeout=25)
            except Exception as bug:
                print(f"requestsDeal Function: {bug}")
                continue

    def write_json_file(self, json_data, json_path):
        with open(json_path, mode='w', encoding='utf-8') as json_file:
            json.dump(json_data, json_file, indent=4, separators=(',',': '))
    
    def read_json_file(self, json_data, json_path):
        data = []
        with open(json_path, mode='r', encoding='utf-8') as json_data:
            data = json.load(json_data)
        return data

    def create_folder(self, folderr_path):
        try: 
            if not os.path.exists(folderr_path):
                os.makedirs(folderr_path)
        except Exception as bug:
            print(f"create_folder Function: {bug}")
            return

    def get_root_dir(self):
        root_path = ''
        if getattr(sys, 'frozen', False):
            root_path = os.path.dirname(sys.executable)
        else:
            try:
                root_path = os.path.dirname(os.path.realpath(__file__))
            except NameError:
                root_path = os.getcwd()
        return root_path

    def main_run(self):
        self.url_list_data = [
            'https://www.douyin.com/user/MS4wLjABAAAAN_oREEJGh0mT9IK1jLnsJQLdy_kFZ51w2VSH0EyafJdh_vcOXR5K8eFMLRt79mMh',
            'https://v.douyin.com/JcjJ5Tq/',
            
            'https://www.douyin.com/user/MS4wLjABAAAAt7VyKvSkkHz_WufLbS8dKIR5tQwCprWUJATHh49BTRU?modal_id=7015104885855112451',
            'https://www.douyin.com/video/7102734573259263271',
            'https://v.douyin.com/FKcep5Y/'
        ]

        for url in self.url_list_data:
            video_data_info = self.get_video_data(url)
            print(video_data_info)
            break

        self.download(video_data_info)
        

def main():
    try:
        douyin = DouYin()
        douyin.main_run()
    except Exception as bug:
        print(f"Main: {bug}")

if __name__ == '__main__':
    main() 