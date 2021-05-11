import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style

# insert serial port information here


plt.axis([-100, 100, -100, 100])
plt.xlabel('X-axis') 
plt.ylabel('Y-axis') 
plt.title('Live End Effector Position') 
circle1 = plt.Circle((0, 0), 50,fill=False, color = 'r')
plt.gca().add_patch(circle1)

for i in range(100):
#while True:
    i = 0
    # insert serial read information here
    #coord = ser.read("",decode)
    #x = coord[0]
    #y = coord[1]

    x_rand = np.random.randint()
    y_rand = np.random.randint()


    plt.scatter(x_rand, y_rand)
    plt.pause(0.05)

    i = i+1



plt.show()
