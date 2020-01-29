import pickle
import matplotlib.pyplot as plt

with open('pickle_chance.pickle', 'rb') as file1:
    data1 =pickle.load(file1)
with open('pickle_vanilla.pickle', 'rb') as file2:
    data2 =pickle.load(file2)

X1 = data1[0]
Y1 = data1[1]

X2 = data2[0]
Y2 = data2[1]

plt.figure()
plt.plot(X1, Y1, label = 'Chance_sampling')
plt.plot(X2, Y2, color = 'red', label = 'Vanilla')
plt.xlabel('Iterations')
plt.ylabel('Value of Player1')
plt.legend(loc='upper right')
plt.show()
