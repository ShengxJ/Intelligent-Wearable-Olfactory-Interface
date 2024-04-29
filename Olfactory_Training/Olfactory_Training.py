# --------------------------------------------------------
# AI-driven personalized olfaction training plan
# Licensed under The MIT License [see LICENSE for details]
# By Shengxin Jia
# Based on PuLP library
# --------------------------------------------------------
import numpy as np
from pulp import *

class Olfactory_Training_Subject:
  def __init__(self,alpha,gamma):
    self.d_list=[]
    self.a_list=[]
    self.y_est=[]
    self.update_list=[]
    self.Q_table=[]
    self.Q_table_0=[]
    self.Q_table_final=[]
    self.update_Q=1
    self.actions=[]
    self.test_=[]
    self.dura_=[]
    self.conf_=[]
    self.a_num=14
    self.m_num=31
    self.test_num=0
    self.scale=1
    self.final_test=7
    self.d_min=1
    self.d_max=60
    self.cost_matrix=[]
    self.timelimit=60
    self.prob=LpProblem("Assignment Problem", LpMinimize)
    self.actions=[]
    self.action_=[]
    self.action_new=[]
    self.new_y_est=[]
    self.alpha = alpha
    self.gamma = gamma

  def estimate_y(self,y_list,actions,Q_table):
    y_est = np.zeros(np.shape(y_list))+y_list
    y_=np.zeros(np.shape(y_list))+y_list
    y_[y_<0]=0
    for i in range(len(actions)):
      if actions[i]>0:
        #print(actions[i],i,Q_table[int(actions[i]*2),i-1,int(y_[i])],y_[i])
        y_est[i] = (Q_table[int(actions[i]*2),i-1,int(y_[i])])/0.75
    return y_est

  def call_cost_matrix(self,y_list,d_list):
    #The matrix who you want to find the maximum rewards
    profit_matrix = np.zeros((self.a_num, self.m_num))
    m_t = np.arange(1,self.m_num+1,1)
    #scale = 3/(d_max-d_min)
    #s_list = 0.5*(1.5*y_1+0.5-np.tanh(np.maximum(0,scale*(d_list-d_min))))
    self.scale = 1/(self.d_max-self.d_min)
    self.s_list = 0.5*(1.5*y_list+0.5*np.maximum(0,y_list)-np.minimum(1,np.maximum(0,self.scale*(d_list-self.d_min))))

    for i in range(self.a_num):
      for j in range(self.m_num):
        d = d_list[m_t[j]]*0.9**i
        if y_list[m_t[j]]>0:
          state=1
        else:
          state=0
        #profit_matrix[i,j] = 0.5*(1.5*y+0.5-np.tanh(np.maximum(0,scale*(d-d_min))))-s_list[m_t[j]]
        profit_matrix[i,j] = self.Q_table[i,j,state]+0.5*(0.5*np.maximum(0,self.Q_table[i,j,state])-np.minimum(1,np.maximum(0,self.scale*(d-self.d_min))))-self.s_list[m_t[j]]
    #Using the maximum value of the profit_matrix to get the corresponding cost_matrix
    max_value = np.max(profit_matrix)
    #Using the cost matrix to find which positions are the answer
    cost_matrix = max_value - profit_matrix
    return cost_matrix

  def initial_Q_table(self,training_effect=1.1):
    Q_table = np.zeros((self.a_num,self.m_num,2))
    Q_table[:,:,0]=Q_table[:,:,0]-3/4
    Q_table[:,:,1]=Q_table[:,:,1]+3/4
    for i in range(self.a_num):
      k=training_effect**i
      if k>1.99:
        Q_table[i:,:,0]=Q_table[i:,:,0]+3/2
        break
    return Q_table

  def update_Q_table(self,actions,y_list,d_list,y_prev,alpha=0.1,gamma=0.8):
    Q_table=np.zeros(np.shape(self.Q_table))+self.Q_table
    m_t=np.arange(1,self.m_num+1,1)
    for j in range(self.m_num):
      state = y_list[m_t[j]]
      state_prev = y_prev[m_t[j]]
      if state_prev>0:
        y_index=1
      else:
        y_index=0
      a_index = int(2*actions[m_t[j]])
      Q_table[a_index,j,y_index]=Q_table[a_index,j,y_index]+self.alpha*(3/4*(state)+self.gamma*self.y_est[m_t[j]]-Q_table[a_index,j,y_index])
      if Q_table[a_index,j,y_index]<self.Q_table[a_index,j,y_index]:
        for i in range(a_index):
          if Q_table[i,j,0]>Q_table[a_index,j,0]:
              Q_table[i,j,0]=Q_table[a_index,j,0]
      if Q_table[a_index,j,y_index]>self.Q_table[a_index,j,y_index]:
          for i in range(a_index+1,self.a_num):
            if Q_table[i,j,0]<Q_table[a_index,j,0]:
              Q_table[i,j,0]=Q_table[a_index,j,0]
    return Q_table

  def solv_assignprob(self,a_t,m_t,timelimit=60.5,j_check=None):
    prob=LpProblem("Assignment Problem", LpMinimize)
    # The cost data is made into a dictionary
    workers = a_t
    jobs = m_t
    costs= makeDict([workers, jobs], self.cost_matrix, 0)

    # Creates a list of tuples containing all the possible assignments
    assign = [(w, j) for w in workers for j in jobs]

    # A dictionary called 'Vars' is created to contain the referenced variables
    vars = LpVariable.dicts("Assign", (workers, jobs), 0, None, LpBinary)

    # The objective function is added to 'prob' first
    prob += (
        lpSum([vars[w][j] * costs[w][j] for (w, j) in assign]),
        "Sum_of_Assignment_Costs",
    )

    # There are row constraints. Each job can be assigned to only one employee.
    for j in jobs:
        prob+= lpSum(vars[w][j] for w in workers) == 1
    # There are workers constrints. total training time limit
    for j in jobs:
        prob+= lpSum(vars[w][j]*w for (w, j) in assign) <=timelimit # 60.5 means 60min
    for w in workers:
        prob+= lpSum(vars[w][j]*(w>=0.5) for (w,j) in assign) >= j_check

    # The problem is solved using PuLP's choice of Solver
    prob.solve()

    # Print the variables optimized value
    for v in prob.variables():
        if v.varValue==1.0:
          print(v.name, "=", v.varValue)

    # The optimised objective function value is printed to the screen
    print("Value of Objective Function = ", value(prob.objective))
    return prob

  def check_assignment(self):
    actions = np.zeros((self.m_num+1))
    for v in self.prob.variables():
        if v.varValue==1.0:
          train_time = float(v.name[7:10])
          job_item = int("".join(i for i in v.name[-2:] if i.isdigit())) # 1 to 31

          actions[job_item] = train_time
    return actions

  def optimize_train_time(self,val_60,a_t,m_t):
    time_check=60
    val_check = 0+val_60
    while val_check-val_60<=1.0:
      time_check=time_check-10
      print('check ',time_check,'min>>>')
      prob_check = self.solv_assignprob(a_t,m_t,time_check,28-np.sum(self.y_[self.y_==1.0]))
      val_check=value(prob_check.objective)
      if time_check<0:
        return 0,0
    #binary search
    lower_limit=0+time_check
    upper_limit=time_check+10
    while (upper_limit-lower_limit)>1:
      time_check = np.floor((lower_limit+upper_limit)/2)
      print('check ',time_check,'min>>>')
      prob_check = self.solv_assignprob(a_t,m_t,time_check,28-np.sum(self.y_[self.y_==1.0]))
      val_check=value(prob_check.objective)
      if val_check>=val_60+1.0:
        lower_limit = 0+time_check
      else:
        upper_limit = 0+time_check
    return upper_limit,lower_limit

  def forward_data_2_Q(self,raw_data):
    test_num = int(1+(np.shape(raw_data)[1]-6)/4)
    self.test_num=test_num
    test_index = [test_num*4-1] if test_num==1 else np.append([4+i*4 for i in range(test_num-1)],test_num*4-1)
    dura_index = [test_num*4] if test_num==1 else np.append([5+i*4 for i in range(test_num-1)],test_num*4)
    action_index = np.array([3+i*4 for i in range(test_num-1)])
    conf_index = [test_num*4+1] if test_num==1 else np.append([6+i*4 for i in range(test_num-1)],test_num*4+1)
    self.test_=raw_data[:,test_index]
    self.dura_=raw_data[:,dura_index]
    self.conf_ = raw_data[:,conf_index]
    if action_index.size>0:
      self.action_=raw_data[:,action_index]
      test_est = np.zeros(np.shape(self.action_))
    self.test_[self.test_==0]=-1
    self.d_max=max(self.dura_[:,-1])
    self.dura_[self.dura_<self.d_min]=self.d_min
    self.dura_[self.dura_>self.d_max]=self.d_max
    self.scale=1/(self.d_max-self.d_min)
    self.Q_table=self.initial_Q_table(training_effect=1.1)
    self.update_list=np.zeros([test_num])+1
    self.update_list[0]=0
    for i in range(1,test_num):
      self.update_Q=self.update_list[i]
      if self.update_Q:
        if i==1:
          self.y_est=self.estimate_y(self.test_[:,-i],self.action_[:,-i],self.Q_table)
          test_est[:,-i] = self.y_est
          self.Q_table = self.update_Q_table(self.action_[:,-i],self.test_[:,-i-1],self.dura_[:,-i-1],self.test_[:,-i],self.alpha,self.gamma)
          self.Q_table_0 = np.zeros(np.shape(self.Q_table))+self.Q_table
          exec("Q_table_%d = np.zeros(np.shape(self.Q_table))+self.Q_table" % (i))
          print('Q_table_%d updated'% i)
        elif i == self.final_test-1:
          self.y_est = np.zeros(np.shape(self.y_est))
          self.Q_table = self.update_Q_table(self.action_[:,-i],self.test_[:,-i-1],self.dura_[:,-i-1],self.test_[:,-i],self.alpha,self.gamma)
          self.Q_table_final = np.zeros(np.shape(self.Q_table))+self.Q_table
        else:
          self.y_est = self.estimate_y(self.test_[:,-i],self.action_[:,-i],self.Q_table)
          test_est[:,-i] = self.y_est
          self.Q_table = self.update_Q_table(self.action_[:,-i],self.test_[:,-i-1],self.dura_[:,-i-1],self.test_[:,-i],self.alpha,self.gamma)
          exec("Q_table_%d = np.zeros(np.shape(self.Q_table))+self.Q_table" % (i))
          print('Q_table_%d updated'% i)

  def check_actioneffectness(self):
    quit_count = 31-np.sum(np.floor(self.new_y_est[self.new_y_est>=1.0]))
    print('agent quit',quit_count+1,'odors', end =" ")
    if quit_count>=10:
      print(' turn to exploit mode>>>')
      self.update_Q=0
      Q_table_ex = self.initial_Q_table(training_effect=1.05)
      self.cost_matrix = self.call_cost_matrix(self.test_[:,0],self.dura_[:,0])
      a_t=np.arange(0,7,0.5)
      m_t = np.arange(1,32,1)
      self.y_=self.test_[:,0]
      j_check = 32-np.sum(self.y_[self.y_==1.0]) if 28-np.sum(self.y_[self.y_==1.0])<15 else None
      self.prob = self.solv_assignprob(a_t,m_t,60,j_check)
      self.action_new = self.check_assignment() #1
      self.new_y_est = self.estimate_y(self.test_[:,0],self.action_new,Q_table_ex)
    else:
      print(' train mode>>>')
      self.update_Q=1

  def action_recommend(self):
    self.cost_matrix = self.call_cost_matrix(self.test_[:,0],self.dura_[:,0])
    a_t=np.arange(0,7,0.5)
    m_t = np.arange(1,32,1)
    self.y_=self.test_[:,0]
    self.prob = self.solv_assignprob(a_t,m_t,60,28-np.sum(self.y_[self.y_==1.0]))
    self.action_new = self.check_assignment() #1
    self.new_y_est = self.estimate_y(self.test_[:,0],self.action_new,self.Q_table)
    lower_limit = 60
    self.check_actioneffectness()
    quit_count = 31-np.sum(np.floor(self.new_y_est[self.new_y_est>=1.0]))
    if self.test_num>=3 and quit_count<=1:
      val_60=value(self.prob.objective)
      upper_limit,lower_limit = self.optimize_train_time(val_60,a_t,m_t)
      if lower_limit<=0:
        lower_limit = np.sum(self.action_[:,0])
      print('training time choice: ',upper_limit,' and ', lower_limit)
      self.prob = self.solv_assignprob(a_t,m_t,lower_limit,28-np.sum(self.y_[self.y_==1.0]))
    self.action_new = self.check_assignment() #1
    self.new_y_est = self.estimate_y(self.test_[:,0],self.action_new,self.Q_table)
    if lower_limit<=30:
      if lower_limit+1>14:
        print('check ',lower_limit+1,' min training plan>>>')
        prob_check = self.solv_assignprob(a_t,m_t,lower_limit+1,28-np.sum(self.y_[self.y_==1.0]))
        if value(prob_check.objective)>value(self.prob.objective):
          self.prob=prob_check
      else:
        print('check ',14,' min training plan>>>')
        self.prob = self.solv_assignprob(a_t,m_t,14,28-np.sum(self.y_[self.y_==1.0]))
      self.action_new = self.check_assignment() #1
      self.new_y_est = self.estimate_y(self.test_[:,0],self.action_new,self.Q_table)
    print('training action with total:',np.sum(test.action_new),'min for ', np.sum(self.action_new>0.),' odor')
    print(self.action_new)
    print('expected training results:')
    print(self.new_y_est)


