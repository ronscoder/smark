import os
import torch

from training_data import TrainingDataModel2

if(os.path.exists('./data/NNModel2')):
    print('loading model')
    model = torch.load('./data/NNModel2')
    correct = 0
    wrong = 0
    for r in TrainingDataModel2.select():
        x = torch.tensor([r.res_coeffs_0, r.res_coeffs_1, r.sup_coeffs_0, r.sup_coeffs_1, r.price_coeffs_0, r.price_coeffs_1,r.price_coeffs_2], dtype=torch.float)
        model.train(mode=False)
        res = model(x)
        values = res.tolist()
        if(r.long == 1):
            print('long   ', [round(x) for x in values])
            if(values[0] == 1):
                correct += 1
            else:
                wrong += 1
        elif(r.short == 1):
            print('short  ', [round(x) for x in values])
            if(values[1]==1):
                correct += 1
            else:
                wrong += 1
        # if(r.wait == 1):
        #     print('nothing', [round(x) for x in values])
        #     if(all([values[2] > x for x in [values[0], values[1]]])):
        #         correct += 1
        #     else:
        #         wrong += 1
            
        
    print('correct', correct, 'wrong', wrong)
        