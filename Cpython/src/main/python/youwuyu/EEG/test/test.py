
def data_test():    # 数据测试
    from torch.utils.data import DataLoader
    from Cpython.src.main.python.youwuyu.EEG.Dataload.eav_deap_cross_dataset import CrossDeapEavDataset
    dataloader = DataLoader(CrossDeapEavDataset(), batch_size=1, shuffle=True)

    i1 = 0
    # d1 = 0
    l1 = 0
    for i, (data, l) in enumerate(dataloader):
        i1 += 1
        if l == 1:
            l1 += 1

    print(i1)   # 总共数据量     # 4.7万
    print(l1)   # 标签为一的量    # 2.5 万

if "__main__" == __name__:
    # data_test()
    # 47000
    # 25864

    data = 1 / (25864 / 47000) * 2
    print(data)
    data = 1 / ((47000 -25864) / 47000) * 2
    print(data)