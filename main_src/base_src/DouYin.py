import os, re, time, sys, json, requests
from Base_APP import *

class DouYin(Base_APP):
    def __init__(self):
        super().__init__()
        self.parent_folder = 'DouYin'
        self.save_path = os.path.join(self.root_dir, self.parent_folder)
    def get_nickname(self):
        pass


    def get_video_data(self, douyin_url, json_output=False):
        video_data_info = []
        real_douyin_url = self.get_real_url(douyin_url)
        url_type = self.get_url_type(real_douyin_url)
        video_index = 1
        if url_type == self.multiple_video_type:
            sec_uid = self.get_sec_uid(real_douyin_url)
            min_cursor = '0'; max_cursor = '0'; done = False
            while not done:
                next_data_api = f'https://www.iesdouyin.com/web/api/v2/aweme/post/?sec_uid={sec_uid}&count=30&max_cursor={max_cursor}&min_cursor={min_cursor}&aid=1128&_signature=PDHVOQAAXMfFyj02QEpGaDwx1S&dytk='
                response = self.requests_deal(next_data_api)

                if response.status_code == 200:
                    js_list_item = response.json()

                    item_list_data = js_list_item['aweme_list']
                    max_cursor = str(js_list_item['max_cursor'])
                    done = not js_list_item['has_more']

                    for video_item in item_list_data:
                        video_id = str(video_item['aweme_id'])
                        try:
                            video_api = 'https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids={}'.format(video_id)
                            js_video = json.loads(self.requests_deal(video_api).text)
                            nickname = str(js_video['item_list'][0]['author']['nickname']) #douyin
                            url_nowatermark = str(js_video['item_list'][0]['video']['play_addr']['url_list'][0]).replace('playwm', 'play') #douyin
                        except Exception as bug:
                            print(f"Nickname, urlNowatermark: {bug}")
                            pass

                        video_data_info.append({
                            'video_index': str(video_index),
                            'video_id': video_id,
                            'nickname': nickname,
                            'video_url': f'https://www.douyin.com/video/{video_id}',
                            'url_nowatermark': url_nowatermark,
                            'save_folder': os.path.join(self.save_path, url_type, nickname),
                        })

                        print(f'>> Video: {video_index:>2} ID: {video_id}')
                        video_index = video_index + 1

        elif url_type == self.video_type:
            video_id = self.get_video_id(real_douyin_url)
            
            try:
                video_api = 'https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids={}'.format(video_id)
                js_video = json.loads(self.requests_deal(video_api).text)
                nickname = str(js_video['item_list'][0]['author']['nickname']) #douyin
                url_nowatermark = str(js_video['item_list'][0]['video']['play_addr']['url_list'][0]).replace('playwm', 'play') #douyin
            except Exception as bug:
                print(f"Nickname, urlNowatermark: {bug}")
                self.write_json_file(js_video,  f'json_mul_video_{video_index}.json')
                pass

            video_data_info.append({
                'video_index': str(video_index),
                'nickname': nickname,
                'video_id': video_id,
                'video_url': f'https://www.douyin.com/video/{video_id}',
                'url_nowatermark': url_nowatermark,
                'save_folder': os.path.join(self.save_path, url_type, nickname),
            })
            
            print(f'>> Video: {video_index:>2} -- ID: {video_id}')
            video_index = video_index + 1
        
        if json_output:
            save_folder = video_data_info[0]['save_folder']
            if len(video_data_info) > 1:
                json_file_path = f'{save_folder}_backup.json'
                self.create_folder(save_folder)
                self.write_json_file(video_data_info, json_file_path)

        return video_data_info

    def main_run(self):
        os.system('cls')

        self.url_list_data = [
            'https://www.douyin.com/user/MS4wLjABAAAAN_oREEJGh0mT9IK1jLnsJQLdy_kFZ51w2VSH0EyafJdh_vcOXR5K8eFMLRt79mMh',
            'https://v.douyin.com/JcjJ5Tq/',
            
            'https://www.douyin.com/video/7102734573259263271',
            'https://www.douyin.com/user/MS4wLjABAAAAt7VyKvSkkHz_WufLbS8dKIR5tQwCprWUJATHh49BTRU?modal_id=7015104885855112451',
            'https://v.douyin.com/FKcep5Y/'
        ]

        for url in self.url_list_data:
            real_url = self.get_real_url(url)
            data = self.get_video_data(url)
            break
        # self.download(user_data_info)

        print(data)
        

def main():
    try:
        douyin = DouYin()
        douyin.main_run()
    except Exception as bug:
        print(f"Main: {bug}")

if __name__ == '__main__':
    main() 