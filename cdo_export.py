
import glob
from datetime import datetime
import json


cdo_dir = "./data/training_cdo/"
path_out = "./data/cdo_exports/"

timestamp = datetime.today().isoformat("_", "seconds")

### FUNCTIONS

def get_history_and_make_dict():
    cdo_list = glob.glob(cdo_dir+'*.json')
    #chat_list.sort(key=file_timestamp, reverse=True)
    #id_title_dict = {x.split('/')[-1][:-5]:'' for x in cdo_list}
    id_path_dict = {x:x.split('/')[-1][:-5] for x in cdo_list}
    id_admin_dict = {}
    for k in id_path_dict.keys():
        try:
            js = read_json_file(k)
            id_admin_dict[k] = js['admin_info']
        except:
            id_admin_dict[k] = {}
    return (id_path_dict, id_admin_dict)



def read_json_file(file):
    with open(file, 'r') as openfile:
        retval = json.load(openfile)
    return retval


def write_json_file(object, path):
    json_object = json.dumps(object)
    with open(f'{path}', 'w') as outfile:
        outfile.write(json_object)


### MAIN
id_path_dict, id_admin_dict = get_history_and_make_dict()

export_json = {}

for path, id in id_path_dict.items():
    file = read_json_file(path)
    export_json[id] = file

filepath = f'./data/cdo_exports/cdo_export_{timestamp}.json'

write_json_file(export_json, filepath)



