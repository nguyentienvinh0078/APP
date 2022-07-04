from collections import UserDict
import os, re, time, sys, json, requests
from tokenize import Name


class TikTok():
    def __init__(self):
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36 Edg/87.0.664.66'
        }

        self.root_dir = self.get_root_dir()
        self.parent_folder = 'TikTok'
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
            file_path = f'{save_folder}\{filename}'
            
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
                    print(f'>> Total: {video_index:2>} / {data_length}')
                    print(f'>> Downloading... [ {filename} ] --')
                    start_download_time = time.time()
                    size = 0; chunk_size = 1024
                    video = self.requests_deal(url_nowatermark)
                    content_size = int(video.headers['content-length'])
                    MB_size = round(content_size / chunk_size / chunk_size, 2)

                    if video.status_code == 200:
                        with open(file=file_path, mode='wb') as file:
                            for data in video.iter_content(chunk_size=chunk_size):
                                file.write(data)
                                size = size + len(data)  
                                print('\r' + '>>%s%.2f%%' % ('>'*int(size*40/content_size), float(size/content_size*100)), end=' ')
                    end_download_time = time.time()
                    total_download_time = end_download_time - start_download_time
                    print(f'\n>> Download time: {total_download_time:.2f}s -- Size: {MB_size:.2f}MB')
                    print('-' * 120)
                    break
                except Exception as bug:
                    print(f"Download: {bug}")
                    continue

    def get_video_data(self, tiktok_url, json_output=False):
        video_data_info = []
        real_tiktok_url = self.get_real_tiktok_url(tiktok_url)
        url_type = self.get_url_type(real_tiktok_url)
        index = 0
        if url_type == self.multiple_video_type:
            nickname = self.get_sec_uid(real_tiktok_url)
            user_id = self.get_user_id(nickname)

            min_cursor = '0'; max_cursor = '0'; done = False
            while not done:
                next_data_api = f'https://www.tiktok.com/share/item/list?id={user_id}&type=1&count=100&maxCursor={max_cursor}&minCursor={min_cursor}'
                response = self.requests_deal(next_data_api)
                
                if response.status_code == 200:
                    js = response.json()

                    item_list_data = js['body']['itemListData']
                    max_cursor = js['body']['maxCursor']
                    done = not js['body']['hasMore']

                    for video_item in item_list_data:
                        video_id = str(video_item['itemInfos']['id'])
                        
                        try:
                            video_api = f'https://api.tiktokv.com/aweme/v1/multi/aweme/detail/?aweme_ids=%5B{video_id}%5D'
                            js = json.loads(self.requests_deal(video_api).text)
                           
                            nickname = str(js["aweme_details"][0]['author']["unique_id"]) #tiktok
                            url_nowatermark = str(js["aweme_details"][0]["video"]["play_addr"]["url_list"][0]) #tiktok
                        except Exception as bug:
                            print(f"nickname, url_nowatermark: {bug}")
                            pass
                        
                        video_data_info.append({
                            'video_index': str(index+1),
                            'video_id': video_id,
                            'nickname': nickname,
                            'video_url': f'https://www.tiktok.com/@{nickname}/video/{video_id}' ,
                            'url_nowatermark': url_nowatermark,
                            'save_folder': os.path.join(self.save_path, url_type, nickname),
                        })

                        print(f'>> Index: {index+1:>2} -- Nickname: {nickname} -- ID: {video_id}')
                        print('-' * 120)
                        index = index + 1

        elif url_type == self.video_type:
            video_id = self.get_video_id(real_tiktok_url)

            try:
                video_api = f'https://api.tiktokv.com/aweme/v1/multi/aweme/detail/?aweme_ids=%5B{video_id}%5D'
                js = json.loads(self.requests_deal(video_api).text)

                nickname = str(js["aweme_details"][0]['author']["unique_id"]) #tiktok
                url_nowatermark = str(js["aweme_details"][0]["video"]["play_addr"]["url_list"][0]) #tiktok
            except Exception as bug:
                print(f"nickname, url_nowatermark: {bug}")
                pass

            video_data_info.append({
                'video_index': str(index+1),
                'video_id': video_id,
                'nickname': nickname,
                'video_url': f'https://www.tiktok.com/@{nickname}/video/{video_id}',
                'url_nowatermark': url_nowatermark,
                'save_folder': os.path.join(self.save_path, url_type, nickname),
            })

            print(f'>> Index: {index+1:>2} -- Nickname: {nickname} -- ID: {video_id}')
            print('-' * 120)
            index = index + 1
        
        if json_output:
            save_path = video_data_info[0]['save_folder']
            if len(video_data_info) > 1:
                json_file_path = f'{save_path}_backup.json'
                self.create_folder(save_path)
                self.write_json_file(video_data_info, json_file_path)

        return video_data_info

    def get_user_id(self, nickname):
        user_id = ""
        user_id_api = 'https://t.tiktok.com/node/share/user/@{}?aid=1988'.format(nickname)
        response = self.requests_deal(user_id_api)
        if response.status_code == 200:
            user_data = response.json()
            try:
                user_id = str(user_data["userInfo"]["user"]["id"])
            except:
                user_id = str(user_data['seoProps']['pageId'])
        return user_id

    def get_url_type(self, real_tiktok_url):
        if '/video/' in real_tiktok_url:
            return self.video_type
        return self.multiple_video_type

    def get_sec_uid(self, real_tiktok_url):
        if '/video/' in real_tiktok_url:
            return re.findall('/video/(\d+)', real_tiktok_url)[0]
        return re.findall('\@(.*)', real_tiktok_url)[0]

    def get_video_id(self, real_tiktok_url):
        if '/video/' in real_tiktok_url:
            return re.findall('/video/(\d+)', real_tiktok_url)[0]
        return ""

    def get_real_tiktok_url(self, tiktok_url):
        real_tiktok_url = ''
        if 'www.tiktok.com' in tiktok_url:
            real_tiktok_url = tiktok_url.split('?')[0]
        elif 'vt.tiktok.com' in tiktok_url:
            response = self.requests_deal(tiktok_url)
            real_tiktok_url = response.url.split('?')[0]
        return real_tiktok_url

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
        os.system('cls')
        self.url_list_data = [
            'https://www.tiktok.com/@yenkim07022004__',
            'https://www.tiktok.com/@yenkim07022004__?is_from_webapp=1&sender_device=pc',
            'https://vt.tiktok.com/ZSdgm4UNs/',

            'https://www.tiktok.com/@yenkim07022004__/video/7104196143575239962?is_from_webapp=1&sender_device=pc&web_id=7077083055764915713',
            'https://www.tiktok.com/@yenkim07022004__/video/7104489383570509083?is_copy_url=1&is_from_webapp=v1',
            'https://vt.tiktok.com/ZSdgmCNn2/?k=1',
        ]

        for url in self.url_list_data:
            user_data_info = self.get_video_data(url)
            print(user_data_info)

            break       

        self.download(user_data_info)

def main():
    try:
        tikTok = TikTok()
        tikTok.main_run()
    except Exception as bug:
        print(f"Main: {bug}")
        os.system('pause')

if __name__ == '__main__':
    main()