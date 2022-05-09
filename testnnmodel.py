import os
import pickle
from direction import get_training_data
# from training_nn import NeuralNetwork
from torch.nn import Sequential
import torch

while(True):
    fpathoffset = 'sample/history_offset'
    histohlcs_offset=None
    if(os.path.exists(fpathoffset)):
        with open(fpathoffset, 'rb') as f:
            histohlcs_offset = pickle.load(f)

    params = get_training_data(histohlcs_offset)
    # print(params)
    #load model

    if(os.path.exists('./data/NNModel2')):
            print('loading model')
            model = torch.load('./data/NNModel2')
            x = torch.tensor([*params['res_coeffs'], *params['sup_coeffs'], *params['price_coeffs']], dtype=torch.float)
            model.train(mode=False)
            res = model(x)
            values = res.tolist()
            print(values)
            print('long:', values[0]>values[1] and values[0] > values[2], 'short:', values[1]>values[0] and values[1]>values[2])

    if(input('stop? y ')):
        print('Goodbye')
        break
