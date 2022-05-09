import torch
from torch import tensor
import torch.nn as nn
import os

class NeuralNetwork(nn.Module):
    def __init__(self) -> None:
        super(NeuralNetwork, self).__init__()

        # parameters
        '''
        inputs
        slopes of SR
        
        '''
        self.inputSize = 7
        self.outputSize = 1
        self.hiddenSize = 7*2
        self.modelfile = './data/NNModel'

        # weights
        self.W1 = torch.randn(self.inputSize, self.hiddenSize)  # 2x3
        self.W2 = torch.randn(self.hiddenSize, self.outputSize)  # 3x1

    def sigmoid(self, s):
        return 1 / (1 + torch.exp(-s))

    def sigmoidPrime(self, s):
        return s * (1 - s)

    def forward(self, X):
        self.z = torch.matmul(X, self.W1)
        self.z2 = self.sigmoid(self.z)
        self.z3 = torch.matmul(self.z2, self.W2)
        o = self.sigmoid(self.z3)
        return o

    def backward(self, X, y, o):
        self.o_error = y - o
        self.o_delta = self.o_error * self.sigmoidPrime(o)
        self.z2_error = torch.matmul(self.o_delta, torch.t(self.W2))
        self.z2_delta = self.z2_error * self.sigmoidPrime(self.z2)
        self.W1 += torch.matmul(torch.t(X), self.z2_delta)
        self.W2 += torch.matmul(torch.t(self.z2), self.o_delta)

    def train(self, X, y):
        o = self.forward(X)
        self.backward(X, y, o)

    def saveWeights(self, model):
        torch.save(model, self.modelfile)

    def predict(self, x):
        return self.forward(x)

# from peewee import *
from training_data import TrainingDataModel
if(__name__=='__main__'):
    while(True):
        # X = []
        # y = []
        if(os.path.exists('./data/NNModel')):
            print('loading model')
            NN = torch.load('./data/NNModel')
        else:
            print('creating model')
            NN = NeuralNetwork()
        # query = TrainingDataModel.select().where(TrainingDataModel.if_trained==False)
        query = TrainingDataModel.select()
        for rec in query:
            # X.append([rec.res_coeffs_0, rec.res_coeffs_1, rec.sup_coeffs_0, rec.sup_coeffs_1, rec.price_coeffs_0, rec.price_coeffs_1, rec.price_coeffs_2])
            # y.append(rec.direction)
            X = [[rec.res_coeffs_0, rec.res_coeffs_1, rec.sup_coeffs_0, rec.sup_coeffs_1, rec.price_coeffs_0, rec.price_coeffs_1, rec.price_coeffs_2]]
            y = [rec.direction]
        # if(any([len(X)==0, len(y)==0])):
        #     print('No training data')
        # else:
            X = torch.tensor(X, dtype=torch.float)
            y = torch.tensor(y, dtype=torch.float)
            for i in range(1000):
                #[1 just for displaying current error
                o = NN(X)
                loss = (y - o)
                rms = torch.mean(loss**2)
                print(f'Loss: {rms.detach().item()}')
                #1]
                NN.train(X, y)
        NN.saveWeights(NN)
        for rec in query:
            rec.if_trained = True
            rec.save()
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
