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
        self.song_path = "."
        self.url = ""
        self.file_list = os.listdir(self.song_path)
        self.down_list = [
            "youtube " + line[-15:-4] + "\n" for line in self.file_list   # REVISE/REMOVE   
        ]  
        self.logger = YtLogger()


        # YoutubeDL Options
        self.ignoreerrors = True
        self.format = 'bestaudio/best'
        self.overwrites = False
        self.download_archive = './logs/downloaded.txt'
        self.output_template = '/%(title)s-%(id)s.%(ext)s'
        self.postprocessors = [{
    		    'key': 'FFmpegExtractAudio',
    		    'preferredcodec': 'vorbis',
    		    'preferredquality': '192',
    		}]

    def download(self):

        ydl_opts = {
			'ignoreerrors': self.ignoreerrors,
			'format': self.format,
			'overwrites': self.overwrites,
			'download_archive': self.download_archive,
			'outtmpl': self.song_path + self.output_template,
			'postprocessors': self.postprocessors,
			'logger': self.logger,
			#'progress_hooks': [yt_hook],
		}

        with open("./logs/downloaded.txt", "w") as down_file:
            down_file.writelines(self.down_list)

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([self.url])

        with open("./logs/errors.txt", "w") as err_file:
            print(f"[info] Download completed with {len(self.logger.errors)} errors")
            err_file.writelines(self.logger.errors)
            print("[info] Errors written to errors.txt")


# CLI
"""
def get_info():
	p_opts = ''.join([f'{key}: {value}\n' for key, value in ydl_opts.items()])

	r_str = f'Directory: {song_path}\n'\
			f'Download link: {url}\n'\
			f'Number of files in directory: {len(os.listdir(song_path))}\n'\
			f'YoutubeDL Options:\n{p_opts}'

	return r_str

def get_args(npt_str, num_required):
	args = npt_str.split(' ')
	if len(args) != num_required:
		print("Wrong number of args. Use 'h' for help.")
		return 
	return args


print('Press enter to download playlist or h for other options.')
while True:
	print('>', end='')
	
	npt = input()
	helpmsg = 'This tool will download a YouTube playlist without overwriting preexisting files.\n'\
			  'OPTIONS:\n'\
			  'h - Prints this message\n'\
			  'd - Download the playlist with the current options\n'\
			  'dir [directory] - Specify new download directory\n'\
			  'l [link] - Change the playlist/download link\n'\
			  'o [option] [value] - Change YoutubeDL Options (May screw things up)\n'\
			  'i - Print the current program options.\n'\
			  'x - Quit the program'

	if npt == 'h':
		print(helpmsg)

	elif npt == '' or npt == 'd':
		download()

	elif npt.startswith('dir'):
		args = get_args(npt, 2)
		if args is None:
			continue
		song_path = args[1]
		print(f"New song directory set: {song_path}")

	elif npt.startswith('l'):
		args = get_args(npt, 2)
		if args is None:
			continue
		url = args[1]
		print(f"New playlist link: '{url}'")

	elif npt.startswith('o'):
		args = get_args(npt, 3)
		if args is None:
			continue
		key, value = args[1:]
		ydl_opts[key] = value
		print(f"New YoutubeDL option set: '{key}': {value}")

	elif npt == 'i':
		print(get_info())

	elif npt == 'x':
		exit()

	else:
		print(f"'{npt}' is not an option. Use 'h' for a list of options.")
"""

# HOOKS
"""
# Output sizes
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
		
"""


# -ciwx:
# -c continue - force resume partially downloaded files
# -i ignore errors# - NOT WORKING - DOWNLOAD STOPS ON ERROR
# -w no overwrites#
# -x extract audio#
# -o path and file#

# OUTPUT ERRORS TO ERRORS.TXT
# USE LOGGER
# CREATE CLI WHERE THESE OPTIONS CAN BE CHANGED
