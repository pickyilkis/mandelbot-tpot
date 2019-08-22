# Modify only these functions for your model
import numpy as np
import pandas as pd
from roarbot.integration.goroar.transform import q_goroar_roarbot, p_roarbot_goroar
from roarbot.models.univariate.tpot import TPOT
from roarbot.datasource import univariate
from roarbot.models import RID, QuestionFactory, Question, QuestionRequest
from datetime import timedelta
from dateutil import parser
## Hyperparamters (Participant can change this to tune their model)
max_size = 100 ## The max size of collected data points
min_size = 10 ## you have to collect more than min_size data point to fit parameters


def on_question(question):
    global models
    contestID = question["responderInfo"]["contestID"]
    test_data = question['units'][0]['value']
    
    print('ContestID:', contestID)
    print('Features:', test_data)
    try:
        roarbot_question = q_goroar_roarbot(question)
        model = models[contestID]
        print('model is ready')
        roarbot_prediction = model.predict(roarbot_question)
        print('roarbot prediction is ready')
 
        goroar_prediction = p_roarbot_goroar(roarbot_prediction, question)
        print(type(goroar_prediction))
        print(goroar_prediction)
        print('The prediction is made using mboa!')
    except Exception as e:
        print('something is wrong')
        print(e)
        goroar_prediction = question
        print('The prediction is the current value!')
    print('Prediction:', goroar_prediction['units'][0]['value'])
    return goroar_prediction


def on_truth(truth_time=None, values=None, contestID = None, **kwargs):
    global model_gens, models, datas, freqs
 
    try:
        model_gens
    except:
        model_gens = {}
    
    try:
        models
    except:
        models = {}
        
    try:
        datas
    except:
        datas = {}
    
    try:
        freqs
    except:
        freqs = {}
    
    try:
        datas[contestID]
    except:
        datas[contestID] = pd.DataFrame(columns=['value'])
 
    datas[contestID].loc[truth_time] = values
 
    if datas[contestID].shape[0] == 2:
        inferred_freq = datas[contestID].index[-1] -  datas[contestID].index[-2]
        if inferred_freq > timedelta(0):
            freqs[contestID] = inferred_freq
        else:
            freqs[contestID] = -inferred_freq
        print('initialized frequency')
    elif datas[contestID].shape[0] > 2:
        inferred_freq = datas[contestID].index[-1] -  datas[contestID].index[-2]
        if inferred_freq > timedelta(0):  
            freqs[contestID] = min(freqs[contestID], inferred_freq)
        print('frequency is: ', freqs[contestID])
        print('type of freq is: ', type(freqs[contestID]) )
        
    print('shape of data is: ', datas[contestID].shape)
    # print('training data is: ', datas[contestID])
    
    if datas[contestID].shape[0] > max_size:
        datas[contestID] = datas[contestID][-max_size:]
    if datas[contestID].shape[0] > min_size:
        print('train using m4 benchmark !!!!!')
        datas[contestID] = datas[contestID].sort_index()
        datas[contestID] = datas[contestID].asfreq(freqs[contestID], method='ffill')
        print('data index after adj: ', datas[contestID].index)
        
        rid = RID.make(contestID)
        ts = univariate.Univariate(datas[contestID]['value'], rid=rid)
        
        print('start training')
        model = TPOT(ts=ts, generations=1, population_size=5)
                                        
        model_gens[contestID] = model
        models[contestID] = model.fit(truth_time)
        print('finish training !!!!!')
    print('ContestID:', contestID, 'Truth_time:', truth_time, 'Quantity:', values)
