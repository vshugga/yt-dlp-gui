# Holds info for QTableWidget and downloader errors
class DownloaderInfo:
    def __init__(self):

        # Columns of table in order
        self.cols = [
            "title",
            "completion",
            "size",
            "speed",
            "downloaded",
            "eta",
            "status",
            "elapsed",
        ]

        # Key = name referred to above, Values = keys of the hook dict
        self.hook_keys = {
            "title": "title",
            "hook_type": "hook_type",
            "size": "_total_bytes_str",
            "eta": "eta",
            "speed": "speed",
            "elapsed": "_elapsed_str",
            "downloaded": "downloaded_bytes",
            "status": "status",
            "completion": "_percent_str",
        }

        # Dict of download data: retains insertion order since python 3.7 (I think)
        # Keys = Vid IDs, Value = video data
        self.hook_data = {}
        self.cur_dl_error = None

    # Return dict of lists or list of lists having row data
    def get_table_data(self):
        table_data = []

        for vid_data in self.hook_data.values():
            r_data = {}  # Row data collected from hook dict; may not be complete

            for name, key in self.hook_keys.items():
                if key not in vid_data:
                    r_data[name] = "-"
                    continue
                r_data[name] = str(vid_data[key])

            table_data.append(r_data)

        data_final = [
            [r_dict[c_name] for c_name in self.cols] for r_dict in table_data]  # Maybe change for readability
        return data_final
