import os, re, time, sys, json, requests
from Base_APP import *

class TikTok(Base_APP):
    def __init__(self):
        super().__init__()
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36 Edg/87.0.664.66'
        }
        self.parent_folder = 'TikTok'
        self.save_path = os.path.join(self.root_dir, self.parent_folder)

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

    def get_video_data(self, tiktok_url, json_output=False):
        video_data_info = []
        real_tiktok_url = self.get_real_url(tiktok_url)
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
            real_url = self.get_real_url(url)
            data = self.get_video_data(url)
            break
        # self.download(user_data_info)

        print(data)

def main():
    try:
        tikTok = TikTok()
        tikTok.main_run()
    except Exception as bug:
        print(f"Main: {bug}")

if __name__ == '__main__':
    main()