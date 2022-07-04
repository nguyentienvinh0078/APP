import os, re, time, sys, json, requests


class Base_APP():
    def __init__(self):
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36 Edg/87.0.664.66'
        }

        self.root_dir = self.get_root_dir()
        self.parent_folder = ''
        self.save_path = os.path.join(self.root_dir, self.parent_folder)
        self.multiple_video_type = 'Multiple Video'
        self.video_type = 'Video'

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

    def create_folder(self, folderr_path):
        try: 
            if not os.path.exists(folderr_path):
                os.makedirs(folderr_path)
        except Exception as bug:
            print(f"create_folder Function: {bug}")
            return

    def write_json_file(self, json_data, json_path):
        with open(json_path, mode='w', encoding='utf-8') as json_file:
            json.dump(json_data, json_file, indent=4, separators=(',',': '))
    
    def read_json_file(self, json_data, json_path):
        data = []
        with open(json_path, mode='r', encoding='utf-8') as json_data:
            data = json.load(json_data)
        return data

    def requests_deal(self, url, max_again=3):
        for again_number in range(max_again):
            try:
                return requests.get(url=url, headers=self.headers, timeout=25)
            except Exception as bug:
                print(f"requestsDeal Function: {bug}")
                continue
    
    def get_url_type(self, real_tiktok_url):
        if '/video/' in real_tiktok_url:
            return self.video_type
        return self.multiple_video_type

    def get_sec_uid(self, real_url):
        if '/video/' not in real_url:
            try:
                # sec_uid douyin
                return re.findall('/user/(.*)', real_url)[0]
            except Exception as bug:
                # sec_uid tiktok = nick name
                return re.findall('\@(.*)', real_url)[0]
        return ""

    def get_video_id(self, real_url):
        if '/video/' in real_url:
            return re.findall('/video/(\d+)', real_url)[0]
        return ""

    def get_real_url(self, url):
        if 'modal_id' in url:
            try:
                video_id = url.split('?')[1].split('=')[1]
            except:
                video_id = url[-19:]
            url = f'https://www.douyin.com/video/{video_id}'

        response = self.requests_deal(url)
        real_url = response.url.split('?')[0]
        return real_url

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

