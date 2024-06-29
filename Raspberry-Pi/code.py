import LED_Array_Pi as arr

d_data = {1: [21, 20, 0x40]}
l_data = {1: [16, 6, 0, 0],
          2: [15, 5, 0, 0],
          3: [17, 4, 0, 0],
          4: [18, 3, 0, 0],
          5: [1, 2, 0, 0],
          6: [2, 1, 0, 0],
          7: [0, 0, 1, 1],
          8: [1, 0, 2, 1],
          9: [2, 0, 3, 1],
          10: [3, 0, 4, 1],
          11: [4, 0, 5, 1]}

d, l = arr.board_connect(d_data, l_data)
brights = [(j / 10)**2 for j in range(0, 11)]
for i in range(1, 31):
    arr.pwm(l, i, 1, 0.25)
