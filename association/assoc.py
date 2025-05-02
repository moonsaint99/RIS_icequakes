import os, glob
import pandas as pd

def assoc_day(date_path = '/Users/rishi/seis/RIS_icequakes/outputs/stalta_detections/20150115'):
    sta_path_list = glob.glob(f"{date_path}/*.csv")
    sta_path_dict = {}
    sta_list = []
    for sta_path in sta_path_list:
        sta_list.append(os.path.basename(sta_path).split('.')[0])
        sta_path_dict[os.path.basename(sta_path).split('.')[0]] = sta_path
    return sta_path_dict

print(assoc_day())