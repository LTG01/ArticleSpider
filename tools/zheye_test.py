from zheye import zheye

z = zheye()
positions = z.Recognize('yzm.jpeg')

print(positions)
print(positions[0])
pos_arr=[]
if len(positions) == 2:
    if positions[0][1] > positions[1][1]:
        pos_arr.append([positions[1][1], positions[1][0]])
        pos_arr.append([positions[0][1], positions[0][0]])
    else:
        pos_arr.append([positions[0][1], positions[0][0]])
        pos_arr.append([positions[1][1], positions[1][0]])
else:
    pos_arr.append([positions[0][1], positions[0][0]])

print(pos_arr)