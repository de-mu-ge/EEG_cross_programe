import os
import random


from Cpython.src.main.python.youwuyu.Video.configs.Configs import Config
eav_dataset_path = Config.eav_dataset_path
# eav_cache_path = Config.eav_cache_path




class Play: # 为了减少使用内存，先这样训练
    def __init__(self, valance, video):
        self.valance = valance
        self.video = video


path_list = []
for m in os.listdir(eav_dataset_path):    # 打开 subject 文件夹
    if m == "GitHub_Codes":
        continue
    # people_list = []
    # for n in os.listdir(os.path.join(eav_dataset_path, m)):    # 打开个人文件夹
    for n in os.listdir(os.path.join(eav_dataset_path, m, 'Video')):
        # people_list.append(n)
        path_list.append(os.path.join(eav_dataset_path, m, 'Video', n))

# print(len(path_list))         # 8400
random.shuffle(path_list)
# input_list = []
# for o in range(200):
#     for i in path_list:
#         input_list.append(i[o])

def add_label(strs):        #标签
    if strs[-9] == 'A' or strs[-9] == 'S':
        return 1    # 表示消极情绪
    else:
        return 0    # 表示非消极情绪