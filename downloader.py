import yt_dlp
import os
from table_info import TableInfo
from threading import Thread, Lock
import json

class YtLogger:
    def __init__(self):
        self.errors = []

    def debug(self, msg):
        if msg.startswith('[download]'):
            print(msg)
        else:
            print(msg)

    def warning(self, msg):
        print(msg)

    def error(self, msg):
        self.errors.append(f'{msg}\n')
        print(msg)


class YtDownloader:
    def __init__(self):
        self.song_path = ""
        self.url = ""
        self.vid_id = None
        self.do_threading = True
        self.thread_locker = None
        self.table_info = TableInfo()
        self.logger = YtLogger()

        # YoutubeDL Options
        self.ignore_errors = True
        self.skip_archived = True # Skip archived downloads
        self.format = 'bestaudio/best'
        self.download_archive = '' #'./logs/download_archive.txt' If not empty, record downloads
        self.error_log = './logs/error_log.txt' # If not empty, record errors
        self.output_template = '/%(title)s-%(id)s.%(ext)s'
        self.add_metadata = True
        self.write_thumbnail = True
        
        # Postprocessors
        self.postprocessors = []
        self.extract_audio = True
        self.audio_codec = 'vorbis'
        self.audio_quality = '192'
        self.embed_thumbnail = True


    def start_download_thread(self, url):
        if self.thread_locker is None:
            self.thread_locker = Lock()

        if not url:
            print('Start download process: No url was provided!')
            return
        
        self.url = url

        d_thread = Thread(target=self._prep_download) 
        d_thread.start()



    def _prep_download(self):
        info_dict = self.get_info()
        if not info_dict:
            print('No urls returned by get_info!')
            return 

        ids_final = self._get_final_ids(info_dict)

        if self.do_threading:
            # THIS PART SHOULD USE THREADING LIMIT (Add the next thread as each is finished)
            threads = [Thread(target=self._download, args=([v_id])) for v_id in ids_final]

            for th in threads:
                th.start()
            for th in threads:
                th.join()
        else:
            self._download(ids_final)
        
        if self.error_log:
            self.write_errors()



    def _download(self, v_ids):

        #for v_id in v_ids:
            #self.table_info.hook_data[v_id] = {}

        try:
            ydl_opts = self.get_options()
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download(v_ids)

            if not self.download_archive:
                return
            if not self.do_threading:
                self.write_download(v_ids)
                return

            self.thread_locker.acquire()
            self.write_download(v_ids)
            self.thread_locker.release()
            
        except Exception as e:
            print(f'Downloader exception: {e}')
            return False

        # Possibly remove table info hook dict here


    def _get_final_ids(self, info_dict):

        if info_dict['extractor'] == 'youtube:tab':
            v_ids = [(entry['id'], entry['title']) for entry in info_dict['entries']]
        else:
            v_ids = [(info_dict['id'], info_dict['title'])]

        ids_final = []
        if self.skip_archived and self.download_archive:
            with open(self.download_archive, "r") as d_file:
                d_list = d_file.readlines()
            for v_id, title in v_ids:
                if f'{v_id}\n' in d_list:
                    print(f'[info] ID: {v_id} already recorded in the archive; {title}')
                    continue
                ids_final.append(v_id)
        else:
            ids_final = [v_id for v_id, title in v_ids]
        
        # Possible one liner for statement above (No print statement)
        #ids_final = [v_id for v_id, title in v_ids if f'{v_id}\n' not in d_list]

        return ids_final



    # Write video ids to download archive (not compatible with yt-dlp archiving)
    def write_download(self, ids):
        try:
            with open(self.download_archive, "a") as d_file:
                for v_id in ids: 
                    d_file.writelines(f'{v_id}\n')
                    print(f"[info] Downloads written to {self.download_archive}")
        except Exception as e:
            print(f'Download archive exception: {e}')



    # Write download errors to error log
    def write_errors(self):
        try:
            n_errs = len(self.logger.errors)
            if n_errs < 1:
                return 
            with open(self.error_log, "a") as err_file:
                err_file.writelines(self.logger.errors)
                print(f"[info] {n_errs} errors written to {self.error_log}")
        except Exception as e:
            print(f'Error log exception: {e}')



    # Get options for downloader
    def get_options(self):
        if self.extract_audio:
            self.postprocessors.append({
    		    'key': 'FFmpegExtractAudio',
    		    'preferredcodec': self.audio_codec,
    		    'preferredquality': self.audio_quality,
    	    })
        if self.add_metadata:
            self.postprocessors.append({
                'key': 'FFmpegMetadata', 'add_metadata': 'True'
            })
        if self.embed_thumbnail:
            self.postprocessors.append({
                'key': 'EmbedThumbnail'
            })

        ydl_opts = {
            'extract_flat': 'in_playlist',
			'ignoreerrors': self.ignore_errors,
			'format': self.format,
			#'overwrites': self.overwrites,
			#'download_archive': self.download_archive,
			'outtmpl': self.song_path + self.output_template,
            'writethumbnail': self.write_thumbnail,
			'postprocessors': self.postprocessors,
			'logger': self.logger,
            'progress_hooks': [self.dl_hook],
            'postprocessor_hooks': [self.pp_hook]
        }

        return ydl_opts  



    
    # Get video/playlist information
    def get_info(self):
        
        ydl_opts = {
            'extract_flat': 'in_playlist',
            'logger': self.logger,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info_dict = ydl.extract_info(self.url, download=False)
                if not info_dict:
                    raise Exception('No info could be gathered.')
                return info_dict

            except Exception as e:
                print(f'Info extraction error: {e}')
                return False
    

    def hook_valid(self, hook, postprocess=False):
        if postprocess:
            if 'postprocessor' not in hook:
                return False
        if 'info_dict' not in hook:
            print('DL Hook: No info dict in hook')
            return False
        if 'id' not in hook['info_dict']:
            print('DL Hook: No ID in hook info dict')
            return False
        return True



    # Set table info with download info, set title
    def dl_hook(self, hook):
        if self.hook_valid(hook):
            title = hook['info_dict']['title']
            hook['title'] = title
            v_id = hook['info_dict']['id']

            self.table_info.hook_data[v_id] = hook
            print(self.table_info.hook_data.keys())

    # Set status with postprocessor info
    def pp_hook(self, hook):
        if self.hook_valid(hook, True): 
            v_id = hook['info_dict']['id']
            pp = hook['postprocessor']

            self.table_info.hook_data[v_id]['status'] = pp



# For testing without UI
if __name__ == '__main__':

    ytdl = YtDownloader()
    #ytdl.url = 'OLAK5uy_m4dSzHl2bwTO6fc5-4VyRk2s5Ycp_FzFg'
    ytdl.song_path =  './test/download'
    ytdl.start_download_thread('9edByCiaLbY')

    

    # Call download:
    # Check if video or playlist


    


    
# Scanning preexisting downloads to update downloaded.txt
'''
self.file_list = os.listdir(self.song_path)
self.down_list = [
    "youtube " + line[-15:-4] + "\n" for line in self.file_list   # REVISE/REMOVE   
] 
with open("./logs/downloaded.txt", "w") as down_file:
    down_file.writelines(self.down_list)
'''
        
