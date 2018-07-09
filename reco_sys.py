import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.parallel
import torch.optim as optim
import torch.utils.data
from torch.autograd import Variable
import pickle
import random

#Getting the data
training_set = pd.read_csv('q1.base', delimiter = '\t')
test_set = pd.read_csv('q1.test', delimiter = '\t')
training_set = np.array(training_set, dtype = 'int')
test_set = np.array(test_set, dtype = 'int')


#Getting total number of users and movies
nb_users = 100
fp = open('document-index.txt', 'rb')
doc_index = pickle.load(fp)
fp.close()
nb_documents = len(doc_index) 
min_user_index = 1
max_user_index  = 100


#Creating User-Movie matrix
def convert(data):
	new_data = []
	global doc_index
	doc_ids = doc_index.values()
	global min_user_index
	global max_user_index
	for id_users in range(min_user_index, max_user_index + 1):
		id_movies = data[:,1][data[:,0] == id_users]
		id_ratings = data[:,2][data[:,0] == id_users]
		ratings = np.zeros(nb_documents)
		ratings[np.array([doc_ids.index(str(i)) for i in id_movies], dtype = 'int')] = id_ratings
		new_data.append(list(ratings))
	return new_data

training_set = convert(training_set)
test_set = convert(test_set)


#Converting data to Torch tensors
training_set = torch.FloatTensor(training_set)
test_set = torch.FloatTensor(test_set)

#Architecture of the Stacked AutoEncoder
class SAE(nn.Module):
	def __init__(self,):
		super(SAE, self).__init__()
		self.fc1 = nn.Linear(nb_documents, 20)
		self.fc2 = nn.Linear(20, 10)
		self.fc3 = nn.Linear(10, 20)
		self.fc4 = nn.Linear(20, nb_documents)
		self.activation = nn.Sigmoid()
	def forward(self, x):
		x = self.activation(self.fc1(x))
		x = self.activation(self.fc2(x))
		x = self.activation(self.fc3(x))
		x = self.fc4(x)
		return x

sae = SAE()
criterion = nn.MSELoss()
optimizer = optim.RMSprop(sae.parameters(), lr = 0.01, weight_decay = 0.5)

#Training the SAE
nb_epoch = 200
for epoch in range(1, nb_epoch + 1):
	train_loss = 0
	s = 0.
	for id_user in range(nb_users):
		input_data = Variable(training_set[id_user]).unsqueeze(0)
		target = input_data.clone()
		if torch.sum(target.data > 0) > 0:
			output = sae.forward(input_data)
			target.require_grad = False
			output[target == 0] = 0
			loss = criterion(output, target)
			mean_corrector = nb_documents/ float(torch.sum(target.data > 0) + 1e-10)
			loss.backward()
			train_loss += np.sqrt(loss.data[0]*mean_corrector)
			s += 1
			optimizer.step()
	print 'epoch: ' + str(epoch) + ' loss: ' + str(train_loss/s)

#Testing the SAE
test_loss = 0
s = 0.
for id_user in range(nb_users):
	input_data = Variable(training_set[id_user]).unsqueeze(0)
	target = Variable(test_set[id_user]).unsqueeze(0)
	if torch.sum(target.data > 0) > 0:
		output = sae.forward(input_data)
		target.require_grad = False
		output[target == 0] = 0
		loss = criterion(output, target)
		mean_corrector = nb_documents/ float(torch.sum(target.data > 0) + 1e-10)
		test_loss += np.sqrt(loss.data[0]*mean_corrector)
		s += 1
print 'test loss: ' + str(test_loss/s)

torch.save(sae, 'my_sae.pt')
		


		
	













