import os
# import torch
import cv2
import numpy as np
import scipy.io as sio
from Cpython.src.main.python.youwuyu.Video.configs.Configs import Config
eav_dataset_path = Config.eav_dataset_path
# eav_cache_path = Config.eav_cache_path

class Play:
    def __init__(self, eeg_data,
                 video_data,
                 audio_data,
                 valance):

        self.eeg_data = eeg_data
        self.video_data = video_data
        self.audio_data = audio_data
        self.valance = valance

# # Get all directories in the parent directory that start with "subject"
# subject_folders = [d for d in os.listdir(parent_directory) if os.path.isdir(os.path.join(parent_directory, d)) and d.startswith("subject")]
#
# # Sort the list
# sorted_subject_folders = sorted(subject_folders, key=lambda s: int(s.replace("subject", "")))
#
# # Check if the sorted list is same as the original list
# is_sorted = subject_folders == sorted_subject_folders

path_list = []
for m in os.listdir(eav_dataset_path):    # 打开 subject 文件夹
    if m == "GitHub_Codes":
        continue
    # for n in os.listdir(os.path.join(eav_dataset_path, m)):    # 打开个人文件夹
    for n in os.listdir(os.path.join(eav_dataset_path, m, 'Video')):
        path_list.append(os.path.join(eav_dataset_path, m, 'Video', n))

# print(len(path_list))
# print(path_list)

def data_read(path_list):
    # if os.path.exists(eav_cache_path):
    #       play_list = np.load(eav_cache_path, allow_pickle=True)
    # else:
    play_list = []
    for path in path_list:
        cap = cv2.VideoCapture(path)

        for _ in range(10):
            video_array = np.zeros([60, 480, 640, 3])

            for i in range(60):
                ret, frame = cap.read()
                # print(ret)
                # print(frame.shape)

                video_array[i] = np.array(frame)


                # print(video_array.shape)

        #         break
        #     break
        # break
            play_list.append(Play(0, video_array, 0, 0))


        # play_list = np.stack(play_list)
        # os.makedirs("cache", exist_ok=True)
        # np.save(eav_cache_path, play_list, allow_pickle=True)

    return play_list



# # 1920 * 1080 * 30
# # 60 * 480 * 640
# print((1920 - 480) / 2)
# print((1080 - 640) / 2)
#
# (B - 480) / 2 : (B - 480) / 2 + 480






































                # while True:
                #     ret, frame = cap.read()
                #     print(np.array(frame).shape)
                #     if not ret:
                #         break


            # fps = cap.get(cv2.CAP_PROP_FPS)  # 30.0      30 fps
            # frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)  # 612.0   总共 612 帧
            # width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)  # 640.0        # 长 640 像素
            # height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)  # 480.0      # 宽 480 像素
            # print(fps,frames , width, height)   # 30.0 612.0 640.0 480.0





            # break

        # play_list = np.stack(play_list)
        # os.makedirs("cache", exist_ok=True)
        # np.save(cache_path, play_list, allow_pickle=True)
        #

    # return play_list

data_read(path_list)






