import yt_dlp
import os
import downloader_info
from threading import Thread, Lock
import json


class YtLogger:
    def __init__(self, dl_inf_obj, err_sig):
        self.errors = []
        self.dl_info = dl_inf_obj
        self.err_signal = err_sig

    def debug(self, msg):
        print(msg)

    def warning(self, msg):
        print(msg)

    def error(self, msg):
        self.errors.append(f"{msg}\n")
        #self.dl_info.cur_dl_error = msg
        self.err_signal.emit(msg)
        print(msg)


class YtDownloader:
    def __init__(self, dl_inf_obj, err_sig, table_sig):
        self.song_path = ""
        self.url = ""
        self.vid_id = None
        self.do_threading = True
        self.thread_locker = Lock()
        self.dl_info = dl_inf_obj
        self.logger = YtLogger(dl_inf_obj, err_sig)
        self.table_signal = table_sig
        self.table_data = {}
        self.is_playlist = False
        self.is_query = False

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
        ydl_opts = self.get_options()  # Do this first to prevent new thread from overwriting
        v_ids = [self.url]
        info_dict = None

        if self.is_playlist:
            info_dict = self.get_info()
            if "entries" in info_dict:
                v_ids = [entry["id"] for entry in info_dict["entries"]]

        if self.skip_archived and self.download_archive:
            if not info_dict:
                info_dict = self.get_info()
            v_ids = self.get_nonarchived(info_dict, v_ids)
        
        '''
        info_dict = {}
        if self.is_playlist: 
            info_dict = self.get_info()
            if not info_dict:
                raise Exception("No urls returned by get_info!")
                return
            ids_final = self._get_final_ids(info_dict)
        else:
            ids_final = self._get_final_ids(info_dict, single_id=)
        '''

        #print(v_ids)
        #print(ydl_opts)

        if self.do_threading:
            # TODO: THREADING LIMIT (Add the next thread as each is finished)
            threads = [
                Thread(target=self._download, args=([v_id], ydl_opts))
                for v_id in v_ids
            ]
            for th in threads:
                th.start()
            for th in threads:
                th.join()
        else:
            self._download(v_ids, ydl_opts)

        if self.error_log:
            print("Logging errors")
            self.write_errors()
            self.logger.errors.clear()

    def _download(self, v_ids, ydl_opts):        
        for v_id in v_ids:
            # Handle duplicate filenames
            table_id = self.get_table_id(v_id)
            self.dl_info.hook_data[table_id] = {"status": "Initializing..."}

            #self.table_data[v_id] = {"status": "Initializing..."}
            #self.table_signal.emit(self.table_data)  # When download finished, set finished?

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download(v_ids)

        for v_id in v_ids:
            if v_id not in self.dl_info.hook_data:
                continue
            self.dl_info.hook_data[v_id]["status"] = "Done"
        
        if not self.download_archive:
            return
        if not self.do_threading:
            self.write_download(v_ids)
            return
        self.thread_locker.acquire()
        self.write_download(v_ids)
        self.thread_locker.release()


        

    def get_nonarchived(self, info_dict, v_ids):
        '''
        if single_id:
            v_ids = [single_id]
        #elif 'extractor' in info_dict:
            #if info_dict["extractor"] == "youtube:tab":
        else:
            v_ids = [entry["id"] for entry in info_dict["entries"]]
        '''
            
        ids_final = []
        with open(self.download_archive, "r") as d_file:
            d_list = d_file.readlines()
            extractor = info_dict["extractor"]
        for v_id in v_ids:
            if f"{extractor} {v_id}\n" in d_list:
                print(f"[info] ID: {v_id} already recorded in the archive")
                continue
            ids_final.append(v_id)
        return ids_final

        # Possible one liner for statement above (No print)
        # ids_final = [v_id for v_id, title in v_ids if f'{v_id}\n' not in d_list]

        return ids_final

    # Write video ids to download archive (not compatible with yt-dlp archiving)
    def write_download(self, ids):
        with open(self.download_archive, "a") as d_file:
            for v_id in ids:
                extractor = self.dl_info.hook_data[v_id]['info_dict']['extractor']
                d_file.writelines(f"{extractor} {v_id}\n")
                print(f"[info] Downloads written to {self.download_archive}")


    # Write download errors to error log
    def write_errors(self):
        n_errs = len(self.logger.errors)
        if n_errs < 1:
            print(f"[info] No errors during download - skip writing to file")
            return
        with open(self.error_log, "a") as err_file:
            err_file.writelines(self.logger.errors)
            print(f"[info] {n_errs} errors written to {self.error_log}")

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
            #"extract_flat": "in_playlist",
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
            #"extract_flat": True,
            "logger": self.logger,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(self.url, download=False)
            if not info_dict:
                raise Exception("No info could be gathered.")
            return info_dict

    # Returns the v_id that should be used in table - handles duplicate entries
    def get_table_id(self, v_id):
        new_id = v_id
        while new_id in self.dl_info.hook_data:
            new_id + "_"
        return new_id
        

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
        if not self.hook_valid(hook):
            return 
        title = hook["info_dict"]["title"]
        hook["title"] = title
        v_id = hook["info_dict"]["id"]



        # Make sure duplicate videos are not overwritten in table (THIS NEEDS MORE WORK)
        #if "first_flag" not in self.dl_info.hook_data['v_id']:
        #    hook["first_flag"] = True
        #    new_id = self.get_table_id(v_id)


        self.thread_locker.acquire()
        self.dl_info.hook_data[v_id] = hook
        self.thread_locker.release()
        #self.table_data[v_id] = hook
        #self.table_signal.emit(self.table_data)

    # Set status with postprocessor info
    def pp_hook(self, hook):
        if not self.hook_valid(hook, True):
            return 
        v_id = hook["info_dict"]["id"]
      
        pp_name = hook["postprocessor"]
        self.thread_locker.acquire()
        self.dl_info.hook_data[v_id]["status"] = pp_name
        self.thread_locker.release()
        #self.table_data[v_id] = hook
        #self.table_signal.emit(self.table_data)




# For testing without UI
if __name__ == "__main__":

    dl_inf = downloader_info.DownloaderInfo()

    ytdl = YtDownloader(dl_inf, err_testsig, table_testsig)
    ytdl.song_path = "./test/download"

    from time import sleep

    #ytdl.url = "qc98u-eGzlc"
    ytdl.url = 'OLAK5uy_m4dSzHl2bwTO6fc5-4VyRk2s5Ycp_FzFg'
    ytdl.start_download_thread()
    sleep(5)
    ytdl.url = "7CH-AjajRCg"
    ytdl.start_download_thread()
