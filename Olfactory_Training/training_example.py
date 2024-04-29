import pandas as pd
import numpy as np

from pulp import *
from Olfactory_Training import *

path = "test.xlsx" 
sheetname = "Sheet1" #Training record file in reverse order
rawdata = pd.read_excel(path,sheetname)
rawdata=rawdata.to_numpy()
test=Olfactory_Training_Subject(0.1,0.9) # setup a training subject
test.forward_data_2_Q(rawdata) # feed training record into the subject
test.action_recommend() # generate training actions based on training record