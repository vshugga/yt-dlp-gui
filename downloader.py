import yt_dlp
import os
#import downloader_info
from threading import Thread, Lock
import json


class YtLogger:
    def __init__(self, dl_inf_obj):
        self.errors = []
        self.dl_info = dl_inf_obj

    def debug(self, msg):
        if msg.startswith("[download]"):
            print(msg)
        else:
            print(msg)

    def warning(self, msg):
        print(msg)

    def error(self, msg):
        self.errors.append(f"{msg}\n")
        self.dl_info.cur_dl_error = msg
        print(msg)


class YtDownloader:
    def __init__(self, dl_inf_obj):
        self.song_path = ""
        self.url = ""
        self.vid_id = None
        self.do_threading = True
        self.thread_locker = Lock()
        self.dl_info = dl_inf_obj
        self.logger = YtLogger(dl_inf_obj)

        # YoutubeDL Options
        self.ignore_errors = True
        self.skip_archived = False  # Skip archived downloads
        self.format = "best"
        self.download_archive = ""  #'./logs/download_archive.txt' If not empty, record downloads
        self.error_log = ""  # If not empty, record errors
        self.output_template = "/%(title)s-%(id)s.%(ext)s"
        self.add_metadata = False

        # Postprocessors
        self.extract_audio = False
        self.audio_codec = "vorbis"
        self.audio_quality = "192"
        self.embed_thumbnail = False
        self.embed_subtitle = False
        self.convert_video = ''


    def start_download_thread(self):
        d_thread = Thread(target=self._prep_download)
        d_thread.start()

    def _prep_download(self):

        ydl_opts = (
            self.get_options()
        )  # Do this first to prevent new thread from overwriting
        info_dict = self.get_info()

        if not info_dict:
            print("No urls returned by get_info!")
            return

        ids_final = self._get_final_ids(info_dict)

        if self.do_threading:
            # TODO: THREADING LIMIT (Add the next thread as each is finished)
            threads = [
                Thread(target=self._download, args=([v_id], ydl_opts))
                for v_id in ids_final
            ]
            for th in threads:
                th.start()
            for th in threads:
                th.join()
        else:
            self._download(ids_final, ydl_opts)

        if self.error_log:
            self.write_errors()
            self.logger.errors.clear()

    def _download(self, v_ids, ydl_opts):
        for v_id in v_ids:
            self.dl_info.hook_data[v_id] = {"status": "Initializing..."}

        #try:
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

        #except Exception as e:
            #raise Exception(e)
            #print(f"Downloader exception: {e}")
            #return False

    def _get_final_ids(self, info_dict):
        if info_dict["extractor"] == "youtube:tab":
            v_ids = [(entry["id"], entry["title"]) for entry in info_dict["entries"]]
        else:
            v_ids = [(info_dict["id"], info_dict["title"])]

        ids_final = []
        if self.skip_archived and self.download_archive:
            with open(self.download_archive, "r") as d_file:
                d_list = d_file.readlines()
            for v_id, title in v_ids:
                if f"{v_id}\n" in d_list:
                    print(f"[info] ID: {v_id} already recorded in the archive; {title}")
                    continue
                ids_final.append(v_id)
        else:
            ids_final = [v_id for v_id, title in v_ids]

        # Possible one liner for statement above (No print)
        # ids_final = [v_id for v_id, title in v_ids if f'{v_id}\n' not in d_list]

        return ids_final

    # Write video ids to download archive (not compatible with yt-dlp archiving)
    def write_download(self, ids):
        #try:
        with open(self.download_archive, "a") as d_file:
            for v_id in ids:
                d_file.writelines(f"{v_id}\n")
                print(f"[info] Downloads written to {self.download_archive}")
        #except Exception as e:
            #raise Exception(e)
            #print(f"Download archive exception: {e}")

    # Write download errors to error log
    def write_errors(self):
        #try:
        n_errs = len(self.logger.errors)
        if n_errs < 1:
            return
        with open(self.error_log, "a") as err_file:
            err_file.writelines(self.logger.errors)
            print(f"[info] {n_errs} errors written to {self.error_log}")
        #except Exception as e:
        #    raise Exception(e)
            #print(f"Error log exception: {e}")

    # Get options for downloader
    def get_options(self):
        pps = []
        if self.extract_audio:
            pps.append(
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": self.audio_codec,
                    "preferredquality": self.audio_quality,
                }
            )

        '''
        convertfs = ['flv', 'mov', 'avi', 'ogg']
        if self.convert_video in convertfs:
            pps.append({"key": "FFmpegVideoConverter",
                        "preferedformat": self.convert_video,
            }) 
        '''
        if self.convert_video:
            pps.append({"key": "FFmpegVideoRemuxer",
                        "preferedformat": self.convert_video,
            })
        
        if self.add_metadata:
            pps.append({"key": "FFmpegMetadata", "add_metadata": "True"})
        if self.embed_thumbnail:
            pps.append({"key": "EmbedThumbnail"})
        #if self.embed_subtitle:
        #    pps.append({"key": "EmbedSubtitle"})

        ydl_opts = {
            "extract_flat": "in_playlist",
            "ignoreerrors": self.ignore_errors,
            "format": self.format,
            "outtmpl": self.song_path + self.output_template,
            "writethumbnail": self.embed_thumbnail,
            "postprocessors": pps,
            "logger": self.logger,
            "progress_hooks": [self.dl_hook],
            "postprocessor_hooks": [self.pp_hook]
            #'overwrites': self.overwrites,
            #'download_archive': self.download_archive,
            #'verbose':True,
        }

        return ydl_opts

    # Get video/playlist information
    def get_info(self):

        ydl_opts = {
            "extract_flat": "in_playlist",
            "logger": self.logger,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            #try:
            info_dict = ydl.extract_info(self.url, download=False)
            if not info_dict:
                raise Exception("No info could be gathered.")
            return info_dict

            
            #except Exception as e:
            #    raise Exception(e)
                #print(f"Info extraction error: {e}")
                #return False

    def hook_valid(self, hook, postprocess=False):
        if postprocess and "postprocessor" not in hook:
            print("DL Hook (Postprocess): No postprocessor in hook")
            return False
        if "info_dict" not in hook:
            print("DL Hook: No info dict in hook")
            return False
        if "id" not in hook["info_dict"]:
            print("DL Hook: No ID in hook info dict")
            return False
        return True

    # Set table info with download info, set title
    def dl_hook(self, hook):
        if self.hook_valid(hook):
            title = hook["info_dict"]["title"]
            hook["title"] = title
            v_id = hook["info_dict"]["id"]
            hook["status"] = hook["status"].capitalize()

            self.dl_info.hook_data[v_id] = hook

    # Set status with postprocessor info
    def pp_hook(self, hook):
        if self.hook_valid(hook, True):
            v_id = hook["info_dict"]["id"]
            pp = hook["postprocessor"].capitalize()

            self.dl_info.hook_data[v_id]["status"] = pp


# For testing without UI
if __name__ == "__main__":

    ytdl = YtDownloader()
    # ytdl.url = 'OLAK5uy_m4dSzHl2bwTO6fc5-4VyRk2s5Ycp_FzFg'
    ytdl.song_path = "./test/download"

    from time import sleep

    ytdl.url = "qc98u-eGzlc"
    ytdl.start_download_thread()
    sleep(5)
    ytdl.url = "7CH-AjajRCg"
    ytdl.start_download_thread()
