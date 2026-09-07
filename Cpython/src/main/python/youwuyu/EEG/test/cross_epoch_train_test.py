# ------------ Train -----------
from Cpython.src.main.python.youwuyu.EEG.configs.Configs import Config
# from Cpython.mian.dataset.Configs import Config
lrs = Config().lrs
# epochs = Config().epochs
epochs = 10

# -------------------------------
from matplotlib import pyplot as plt
import numpy as np
# import torch
from torch.utils.data import DataLoader
# from Cpython.mian.dataset.dataset import TrainEegDataset, TestEegDataset
# from Cpython.mian.dataset.DataRead import Play
from Cpython.src.main.python.youwuyu.EEG.Dataload.eav_deap_cross_dataset import CrossDeapEavDataset, TextCrossDeapEavDataset, TrainExamCrossDeapEavDataset
# from Cpython.main.EEG.Dataload.dataset import TrainEegDataset, TestEegDataset
import torch
# train_dataset = CrossDeapEavDataset()
# test_dataset = TextCrossDeapEavDataset()

train_dataloader = DataLoader(CrossDeapEavDataset(), batch_size=64, shuffle=True)
train_dataloader_iter = DataLoader(TrainExamCrossDeapEavDataset(), batch_size=1, shuffle=False)
test_dataloader = DataLoader(TextCrossDeapEavDataset(), batch_size=1, shuffle=False)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# --------------------- 获取模型 -------------------------
# from Cpython.src.main.python.youwuyu.EEG.model.cross_deap_eav_model import Model
# model = Model()
# from Cpython.src.main.python.youwuyu.EEG.model.cross_deap_eav_model import CrossModel
# model = CrossModel()
# from Cpython.src.main.python.youwuyu.EEG.model.cross_deap_eav_model import  EEGClassifier
# model = EEGClassifier()

from Cpython.src.main.python.youwuyu.EEG.model.transformer_deap_eav_cross_model import EEGModel
model = EEGModel()

# model.train()
model.to(device)

# -----------真实评价标准--------------
class ExamNum:
    def __init__(self):
        self.num = 0    # 总数
        self.net = 0
        self.true = 0
        self.net_true = 0
        # self.pos = 0
        # self.neg = 0


# class_counts = torch.tensor([       # 加权
#     440,   # class 0
#     1068,  # class 1
#     844,   # class 2
#     828,   # class 3
#     800,   # class 4
#     452,   # class 5
#     292,   # class 6
#     268,   # class 7
#     108,   # class 8
#     20     # class 9
# ], dtype=torch.float32)
#
# weights = 1.0 / torch.sqrt(class_counts)
# weights = weights / weights.mean()
# weights = weights.to(device)

optimizer = torch.optim.Adam(model.parameters(), lr=lrs, weight_decay=1e-3)
criterion = torch.nn.CrossEntropyLoss()

# print("模型训练开始")

# train_mat = []
# test_mat = []
exam_num_list = []

for epoch in range(epochs):

    model.train()   # 找到模型学习不动的原因,忘记改回train()

    print("Epoch [{}/{}]".format(epoch + 1, epochs))
    # print("是否有进循环")
    items = 0

    for i, (data, labels) in enumerate(train_dataloader):


        # --------------噪声--------------------
        # num = (0.01 * torch.randn([24, 32, 2016])).float().to(device)


        data = data.to(device)

        # --------------添加噪声--------------------
        # data += num

        labels = labels.to(device)

        optimizer.zero_grad()
        outputs = model(data)
        loss = criterion(outputs, labels)

        items += loss.item()

        loss.backward()
        optimizer.step()

        # break

    print("")
    print("")
    print("epoch:", epoch)
    print("loss:", items / len(train_dataloader))

    model.eval()

    # result = []


    for data in [train_dataloader_iter, test_dataloader]:

        # true = 0        # 重新积累
        # false = 0
        # index = 0
        exam_num = ExamNum()

        for i, (inputs, labels) in enumerate(data):
            # index += 1
            exam_num.num += 1   # 计数器+=1

            inputs, labels = inputs.to(device), labels.to(device)

            outputs = model(inputs)
            outputs = outputs.cpu().detach().numpy()
            outputs = np.argmax(outputs, axis=1).tolist()[0]

            # print(type(label))
            # print(label)
            labels = int(labels)


            if labels == 0:
                exam_num.net += 1  # 消极计数加一
                if outputs == labels:
                    exam_num.net_true += 1

            if outputs == labels:
                exam_num.true += 1  # 预测正确加一


        # 由于生理层面的漏报的损失远大于误报，采用负面召回率
        exam_net_true_nums = exam_num.net_true / exam_num.net       # 医学负面召回率
        exam_true_num = exam_num.true / exam_num.num        # 全局准确率

        # print("epoch:", epoch)
        print("训练集 / 测试集:")
        print("召回率:", exam_net_true_nums)
        print("准确率:", exam_true_num)

        exam_num_list.append(exam_net_true_nums)      # 叠加
        exam_num_list.append(exam_true_num)



print(exam_num_list[0::4])
print(exam_num_list[2::4])

plt.plot(exam_num_list[0::4])
plt.plot(exam_num_list[2::4])
plt.show()

































            # print("label的结构 ")
            # print(label)
            # break

            # label = torch.sigmoid(label).cpu().detach().numpy()
            # label = np.argmax(label, axis=1)[0]

            # print(out == label, out, label)

            # if label == out:
            #
            #     true += 1
            # else:
            #     false += 1

            # if index % 100 == 0:
            #     # true = true + 1
            #     print("")
            #     print("")
                # print(str(data))
                # print(label, out)


                # if label == out or label == out + 1 or label == out - 1:
                #     true += 1
                # else:
                #     false += 1


            # ------------测试------------
            # if i % 100 == 0:
            #     print("模型输出")
            #     print(out, label)
            # ------------end--------------








    #         if label == out:
    #             true += 1
    #         else:
    #             false += 1
    #
    #     result.append(true / index)
    #
    # train_mat.append(result[0])
    # test_mat.append(result[1])
    #
    # print("训练集结果:", result[0])
    # print("测试集结果:", result[1])
    # print('')
    # print('')
    # print('')




