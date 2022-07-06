import yt_dlp
import os
from multiprocessing import Process, Lock

class YtLogger:
    def __init__(self):
        self.errors = []

    def debug(self, msg):
        if msg.startswith("[download]"):
            print(msg, end="\r")
        else:
            print(msg)

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
        self.vid_id = None
        self.do_threading = True

        # YoutubeDL Options
        self.ignore_errors = True
        self.skip_archived = True # Skip archived downloads
        self.format = 'bestaudio/best'
        self.download_archive = './logs/download_archive.txt' # If not empty, record downloads
        self.error_log = './logs/error_log.txt'
        self.output_template = '/%(title)s-%(id)s.%(ext)s'
        self.add_metadata = True
        self.write_thumbnail = True
        
        # Postprocessors
        self.postprocessors = []
        self.extract_audio = True
        self.audio_codec = 'vorbis'
        self.audio_quality = '192'
        self.embed_thumbnail = True


    def download(self):
        info_dict = self.get_info()
        if not info_dict:
            print('No urls returned by get_info!')
            return 

        if info_dict['extractor'] == 'youtube:tab':
            vids = [(entry['id'], entry['title']) for entry in info_dict['entries']]
        else:
            vids = [(info_dict['id'], info_dict['title'])]

        ids_final = []
        if self.skip_archived:
            with open(self.download_archive, "r") as d_file:
                d_list = d_file.readlines()
            for v_id, title in vids:
                if f'{v_id}\n' in d_list:
                    print(f'[info] ID: {v_id} already recorded in the archive; {title}')
                    continue
                ids_final.append(v_id)
        

        if self.do_threading:
            lock = Lock()

            # THIS PART SHOULD USE THREADING LIMIT (Add the next process as each is finished)
            processes = [Process(target=self.__download, args=(v_id, lock,)) for v_id in ids_final]

            for p in processes:
                #yt_process = Process(target=self.__download, args=(v_id, lock,)) 
                #yt_process.start()
                p.start()
            
            for p in processes:
                p.join()
        else:
            self.__download(ids_final)
            
        self.write_errors()



    def __download(self, url, lock=None):
        try:
            ydl_opts = self.get_options()
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download(url)

            if lock is None:
                self.write_download(url)
                return
            lock.acquire()
            self.write_download(url)
            lock.release()
            

        except Exception as e:
            print(f'Downloader exception: {e}')
            return False


    def write_download(self, vid_id):
        try:
            with open(self.download_archive, "a") as d_file:
                d_file.writelines(f'{vid_id}\n')
                print(f"[info] Downloads written to {self.download_archive}")
        except Exception as e:
            print(f'Download archive exception: {e}')


    def write_errors(self):
        try:
            n_errs = len(self.logger.errors)
            print(f"[info] Download completed with {n_errs} errors")
            if n_errs < 1:
                return 
            with open(self.error_log, "a") as err_file:
                err_file.writelines(self.logger.errors)
                print(f"[info] Errors written to {self.error_log}")
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
			#'progress_hooks': [yt_hook],
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
            

# For testing without UI
if __name__ == '__main__':

    ytdl = YtDownloader()
    ytdl.url = 'OLAK5uy_m4dSzHl2bwTO6fc5-4VyRk2s5Ycp_FzFg'
    ytdl.song_path =  './test/download'
    ytdl.download()
    #print(ytdl.get_info())

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
        

# HOOKS

'''
progbar_len = 10
max_name_len = 50

def yt_hook(hook):
	if hook['status'] == 'finished':
		
		print('[Finished downloading]', hook['filename'])
		print('[Converting...]', end='\r')
		

	elif hook['status'] == 'downloading':
		
		dbytes = hook['downloaded_bytes']
		tbytes = hook['total_bytes']
		name = hook['filename']
		
		bar = progbar_len * dbytes // tbytes
		space = progbar_len - bar
		prog_str = '['+'#'*bar+' '*space+']'
		
		if len(name) > max_name_len:
			name = name[:max_name_len-3] + '...'
		
		print('[Downloading]', name, ':', str(dbytes) + '/' + str(tbytes), prog_str, end='\r')
'''
