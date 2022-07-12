


# Holds info for QTableWidget
class TableInfo:
    
    def __init__(self):

        # Columns of table in order
        self.cols = [
            'title', 
            'completion', 
            'size', 
            'speed', 
            'downloaded', 
            'eta', 
            'status', 
            'elapsed'
        ]

        # Key = name referred to above, Values = keys of the hook dict 
        self.hook_keys = {
            'title':'title',
            'hook_type':'hook_type',
            'size':'_total_bytes_str',
            'eta':'eta',
            'speed':'speed',
            'elapsed':'_elapsed_str',
            'downloaded':'downloaded_bytes',
            'status':'status',
            'completion':'_percent_str',
        }

        # Dict of download data: retains insertion order
        # Keys = Vid IDs, Value = video data
        self.hook_data = {}

   

    '''
    def __iter__(self):
        self.index = 0
        return self

    def __next__(self):
        if self.index >= len(hook_data):
            raise StopIteration
    '''

        



    # Return dict of lists or list of lists having row data
    def get_table_data(self):
        #table_list = []

        table_data = [] 


        for vid_data in self.hook_data.values():
            #row_list = []
            r_data = {} # Row data collected from hook dict; may not be complete

            for name, key in self.hook_keys.items():
                if key not in vid_data:
                    r_data[name] = '-'
                    continue
                r_data[name] = str(vid_data[key])
            
            '''
            if 'info_dict' in r_data:
                if 'title' in r_data['info_dict']:
                    r_data['title'] = r_data['info_dict']['title']

            if r_data['postprocessor'] != '-':
                r_data['status'] = r_data['postprocessor']
            '''

            table_data.append(r_data)

        '''
        return_list = []
        for r_dict in table_data:
            row_list = []
            for c_name in self.cols:
                row_list.append(r_dict[c_name])
            return_list.append(row_list)
        '''

        l = [[r_dict[c_name] for c_name in self.cols] for r_dict in table_data]
        return l



        #return [[data_str for data_str in row_dict.values()] for row_dict in table_data]


