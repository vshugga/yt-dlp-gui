# Holds info for QTableWidget and downloader errors
class DownloaderInfo:
    def __init__(self):

        # Columns of table (IN ORDER DISPLAYED)
        self.cols = [
            "title",
            "completion",
            "size",
            "downloaded",
            "speed",
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

        # Don't overwrite these columns with hyphens
        '''
        self.hyphen_exclusion = [
            'title',
            'size',
            'elapsed',
            'downloaded',
            'status',
            'completion',
        ]
        '''
        
        # Dict of download data: retains insertion order since python 3.7 (I think)
        # Keys = Vid IDs, Value = video data
        self.hook_data = {}

    # Return list of lists having row data from the current hook_data
    def get_table_data(self, hook_data=None):
        if not hook_data:
            hook_dict = self.hook_data
        else:
            hook_dict = hook_data
        
        if not hook_dict:
            return

        table_data = []

        for v_id, vid_data in hook_dict.items():
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
