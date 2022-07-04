import yt_dlp
import os


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
        self.extractor = None

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

    def get_options(self):
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

    def download(self, url, lock):
        try:
            ydl_opts = self.get_options()
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download(url)

            lock.acquire()

            if self.download_archive:
                with open(self.download_archive, "w") as d_file:
                    d_file.writelines(f'{self.extractor} {self.vid_id}')
                    print(f"[info] Downloads written to {self.download_archive}")
            if self.error_log:
                with open(self.error_log, "w") as err_file:
                    print(f"[info] Download completed with {len(self.logger.errors)} errors")
                    err_file.writelines(self.logger.errors)
                    print(f"[info] Errors written to {self.error_log}")

            lock.release()

        except Exception as e:
            print(f'Downloader error: {e}')
            return False

    # Get video/playlist info, check if already downloaded
    def get_info(self):
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

        
        
        # Scanning preexisting downloads to update downloaded.txt
        '''
        self.file_list = os.listdir(self.song_path)
        self.down_list = [
            "youtube " + line[-15:-4] + "\n" for line in self.file_list   # REVISE/REMOVE   
        ] 

        with open("./logs/downloaded.txt", "w") as down_file:
            down_file.writelines(self.down_list)
        '''
        ydl_opts = self.get_options()

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info_dict = ydl.extract_info(self.url, download=False)
                if not info_dict:
                    raise Exception('No info could be gathered.')
                
                #print('TEST')

                self.extractor = info_dict['extractor']
                self.vid_id = info_dict['id']
                #print(info_dict)

                # WHEN PLAYLIST
                if self.extractor == 'youtube:tab':
                    vid_ids = [entry['id'] for entry in info_dict['entries']]
                    return vid_ids

                if self.skip_archived:
                    with open(self.download_archive, "r") as d_file:
                        d_list = d_file.readlines()

                    if f'{self.extractor} {self.vid_id}' in d_list:
                        print(f'{info_dict["title"]} is already recorded in the archive.')
                        return False

                #self.download()
            except Exception as e:
                print(f'Downloader error: {e}')
                return False
            
            return [self.url]

    

# HOOKS


#progbar_len = 10
#max_name_len = 50
#
#def yt_hook(hook):
#	if hook['status'] == 'finished':
#		
#		print('[Finished downloading]', hook['filename'])
#		print('[Converting...]', end='\r')
#		
#
#	elif hook['status'] == 'downloading':
#		
#		dbytes = hook['downloaded_bytes']
#		tbytes = hook['total_bytes']
#		name = hook['filename']
#		
#		bar = progbar_len * dbytes // tbytes
#		space = progbar_len - bar
#		prog_str = '['+'#'*bar+' '*space+']'
#		
#		if len(name) > max_name_len:
#			name = name[:max_name_len-3] + '...'
#		
#		print('[Downloading]', name, ':', str(dbytes) + '/' + str(tbytes), prog_str, end='\r')
		



# -ciwx:
# -c continue - force resume partially downloaded files
# -i ignore errors# - NOT WORKING - DOWNLOAD STOPS ON ERROR
# -w no overwrites#
# -x extract audio#
# -o path and file#

# OUTPUT ERRORS TO ERRORS.TXT
# USE LOGGER
# CREATE CLI WHERE THESE OPTIONS CAN BE CHANGED