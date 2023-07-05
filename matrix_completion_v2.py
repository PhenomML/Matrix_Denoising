# -*- coding: utf-8 -*-
"""Matrix_completion_v2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1aoQ1U_QaI9ioFtyEvTcF6L3dp07nERV4
"""

# general imports
import numpy as np
import pandas as pd

# main function

def get_measurements(n, Lambda, p, mc_number):

  # input dataframe
  input = pd.DataFrame(columns='n, Lambda, p, mc_number'.split(', '))
  input.loc[0] = n, Lambda, p, mc_number

  # get primary data
  np.random.seed(mc_number)
  u, v, M, noise, obs_inds = make_primary_data(n, Lambda, p)

  # make observation
  Y = Lambda * M + noise

  # solve nuclear norm minimization
  Mhat = minimize_nuclear_norm(Y=Y, observed=obs_inds)

  # take primary measuremensts
  output = pd.DataFrame(columns=['cosL', 'cosR'])
  output.loc[0] = get_cos(Mhat, u, v)

  # take secondary maesurments
  def sin_from_cos(x):
    return np.sqrt(1 - x**2)

  output['sinL'] = sin_from_cos(output['cosL'])
  output['sinR'] = sin_from_cos(output['cosR'])
  output['1/sinL'] = 1 / output['sinL']
  output['1/sinR'] = 1 / output['sinR']


  return pd.concat([input, output], axis=1)

# import required libraries
import cvxpy
from cvxpy.atoms import normNuc, multiply, norm
from sklearn.utils.extmath import randomized_svd

# othe functions

def make_primary_data(n, Lambda, p):

  u, v = np.random.normal(size=(2, n))
  u /= np.linalg.norm(u)
  v /= np.linalg.norm(v)

  M = np.outer(u, v)

  noise = np.random.normal(0, 1/np.sqrt(n), (n, n))
  obs_inds = np.random.binomial(1, p, size=(n, n))

  return  u, v, M, noise, obs_inds


def minimize_nuclear_norm(Y, observed):
  X = cvxpy.Variable(Y.shape)
  objective = cvxpy.Minimize(normNuc(X))
  Z = multiply(X - Y, observed)

  constraints = [Z == 0]
  prob = cvxpy.Problem(objective, constraints)

  prob.solve()

  return X.value

def get_cos(Mhat, u, v):

  def veccos(v, vhat):
    return np.abs(np.inner(v, vhat))[0]

  uhat, snrhat, vhat = randomized_svd(Mhat, n_components=1)
  uhat = uhat.T

  cosL = veccos(u, uhat)
  cosR = veccos(v, vhat)

  return cosL, cosR

# test single run
n, Lambda, p, mc_number = 20, 1, .5, 1
print(get_measurements(n, Lambda, p, mc_number))

# test run and record

# from google.colab import drive
# from os import mkdir, path
# drive.mount('/content/gdrive/')
# %cd 'gdrive/MyDrive/low_rank_completion/'


# folder = 'test_run_July_4/'
# if not path.exists(folder):
#   mkdir(folder)

# add = folder + 'records.csv'
# for n in [10, 20]:
#   for Lambda in np.arange(1, 5, 1):
#     for p in [.5, .25, 1]:
#       for mc_num in range(5):

#         df = get_measurements(n=n, Lambda=Lambda, p=p, mc_number=mc_num)
#         if path.exists(add):
#           mode = 'a'
#           header = False
#         else:
#           mode = 'w'
#           header = True
#         df.to_csv(add, mode=mode, index=False, header=header)