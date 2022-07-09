import yt_dlp
import os
from multiprocessing import Process, Lock

import json

class YtLogger:
    def __init__(self):
        self.errors = []

    def debug(self, msg):
        if msg.startswith("[download]"):
            print(msg, end="\r")
        else:
            print(msg)
#with open('plistinfogeneric.json', 'w') as haha:
    #    json.dump(info_dict, haha)
    def warning(self, msg):
        print(msg)

    def error(self, msg):
        self.errors.append(msg + "\n")
        print(msg)


class YtDownloader:
    def __init__(self):
        self.song_path = ""
        self.url = ""
        self.logger = YtLogger()
        self.table_updater = None
        
        self.vid_id = None
        self.do_threading = True

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


    def request_download(self, url):
        self.url = url
        lock = Lock()
        download_process = Process(target=self.download, args=(lock,)) 
        download_process.start()


    def download(self, lock):
        info_dict = self.get_info()
        if not info_dict:
            print('No urls returned by get_info!')
            return 

        if info_dict['extractor'] == 'youtube:tab':
            v_ids = [(entry['id'], entry['title']) for entry in info_dict['entries']]
        else:
            v_ids = [(info_dict['id'], info_dict['title'])]


        # NEEDS REWRITTEN TO TRIGGER WHEN NOT ARCHIVING
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
        
        # Possible one liner for statement above
        #ids_final = [v_id for v_id, title in v_ids if f'{v_id}\n' not in d_list]


        if self.do_threading:
            # THIS PART SHOULD USE THREADING LIMIT (Add the next process as each is finished)
            processes = [Process(target=self.__download, args=([v_id], lock,)) for v_id in ids_final]

            for p in processes:
                #yt_process = Process(target=self.__download, args=(v_id, lock,)) 
                #yt_process.start()
                p.start()
            
            for p in processes:
                p.join()
        else:
            self.__download(ids_final)
        
        if not self.error_log:
            return

        self.write_errors()


    def __download(self, ids, lock=None):
        try:
            ydl_opts = self.get_options()
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download(ids)

            if not self.download_archive:
                return
            if lock is None:
                self.write_download(ids)
                return

            lock.acquire()
            self.write_download(ids)
            lock.release()
            

        except Exception as e:
            print(f'Downloader exception: {e}')
            return False


    def write_download(self, ids):
        try:
            with open(self.download_archive, "a") as d_file:
                for v_id in ids: 
                    d_file.writelines(f'{v_id}\n')
                    print(f"[info] Downloads written to {self.download_archive}")
        except Exception as e:
            print(f'Download archive exception: {e}')


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
			'progress_hooks': [self.yt_hook]
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

                #self.download()
            except Exception as e:
                print(f'Info extraction error: {e}')
                return False
    
    # Update table with needed info
    def yt_hook(self, hook):
        if self.table_updater is None:
            print('Table update method not set!')
            return

        info = hook['info_dict']
        table_data = [{
            'title':info['title'],
            'size':hook["_total_bytes_str"],
            'eta':'TEST ETA',
            'speed':'TEST SPEED',
            'elapsed':hook['_elapsed_str'],
            'downloaded':hook['downloaded_bytes'],
            'status':hook['status'],
            'completion':hook['_percent_str']
        }]

        update_table = Process(target=self.table_updater, args=([table_data],))
        update_table.start()
        self.table_updater(table_data)

        #table_process = Process(target=self.table_updater, args=([table_data]))
        #table_process.start()

        #with open('hook_data.json', 'w') as file:
        #    json.dump(hook, file)
        #return hook['status']




# For testing without UI
if __name__ == '__main__':

    ytdl = YtDownloader()
    ytdl.url = 'OLAK5uy_m4dSzHl2bwTO6fc5-4VyRk2s5Ycp_FzFg'
    ytdl.url = '9edByCiaLbY'
    ytdl.song_path =  './test/download'
    ytdl.download()

    

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
        
