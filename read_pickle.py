import pickle
import matplotlib.pyplot as plt

with open('pickle_vanilla.pickle', 'rb') as file:
    data =pickle.load(file)

X1 = []
Y1 = []

X2 = data[0]
Y2 = data[1]

plt.figure()
plt.plot(X1, Y1, label = 'Chance_sampling')
plt.plot(X2, Y2, color = 'red', label = 'Vanilla')
plt.xlabel('Iterations')
plt.ylabel('Value of Player1')
plt.legend(loc='upper right')
plt.show()
