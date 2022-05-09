import torch
from torch import tensor
import torch.nn as nn
import os


# from peewee import *
from training_data import TrainingDataModel2
if(__name__=='__main__'):
    while(True):
        if(os.path.exists('./data/NNModel2')):
            print('loading model')
            model = torch.load('./data/NNModel2')
        else:
            print('creating model')
            # model = nn.Sequential(nn.Linear(7, 200), nn.Linear(200,200), nn.Linear(200,50), nn.Linear(50,3), nn.Sigmoid())
            model = nn.Sequential(nn.Linear(7, 200),nn.ReLU(), nn.Linear(200,50), nn.Linear(50,3), nn.Softmax(dim=0))
            # output, long, short, wait 
        X = []
        y = []
        # query = TrainingDataModel2.select().where(TrainingDataModel2.if_trained==False)
        query = TrainingDataModel2.select()
        for rec in query:
            X.append([rec.res_coeffs_0, rec.res_coeffs_1, rec.sup_coeffs_0, rec.sup_coeffs_1, rec.price_coeffs_0, rec.price_coeffs_1, rec.price_coeffs_2])
            # y = [[rec.long, rec.short, rec.wait]]
            y.append([rec.long, rec.short, rec.wait])
        if(not 0 in [len(X), len(y)]):
            X = torch.tensor(X, dtype=torch.float)
            y = torch.tensor(y, dtype=torch.float)
            lossfn = nn.MSELoss(reduction='mean')
            optimizer = torch.optim.RMSprop(model.parameters(), lr=1e-2)
            epochs = 500
            for e in range(epochs):
                optimizer.zero_grad()
                model.train(mode=True)
                predicted = model(X)
                loss = lossfn(predicted, y)
                print('training ', e, end="\r")
                loss.backward()
                optimizer.step()
                # optimizer.zero_grad()
            print('done', ' '*50)
            rec.if_trained = True
            rec.save()
            torch.save(model,'./data/NNModel2')
        res = input('stop training=x? ')
        if(res=='x'):
            print('done')
            break


    # next = True
    # # user interaction mode
    # while next:
    #     study = float(input('Study hour: '))
    #     sleep = float(input('Sleep hour: '))
    #     xPredict = torch.tensor(([study, sleep]), dtype=torch.float)
    #     # xPredict_max, _ = torch.max(xPredict, 0)
    #     xPredictScaled = xPredict / X_max
    #     result = NN.predict(xPredictScaled)
    #     print(f'[{study}, {sleep}] result: {(result * y_max).item()}')
    #     # if(input('next? ')!=''):
    #     #     next = False
