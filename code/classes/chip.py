import numpy as np
import plotly
import plotly.plotly as py
import plotly.graph_objs as go
import sys


plotly.tools.set_credentials_file(username='zhongyuchen', api_key='MVlLKp3ujiU1bFQImbKP')


four_direction = [[1, 0], [-1, 0], [0, 1], [0, -1]]


class chip:
    # data structure
    # cnt_wire = 0
    grid = []
    gate = []
    net = []
    wire = []
    used_wired = []
    size = []

    map_line = []

    def __init__(self, size, gatelist, netlist):
        # line number
        # self.cnt_wire = 0
        self.wire = []
        # 3D grid -> -1: gate, 0: available, > 0: wire number

        self.net = netlist

        self.grid = np.zeros([size[0], size[1], size[2]])
        self.size = size
        # size[0] shows level, size[1] shows row, size[2] shows column

        self.used_wired = [[[-1 for i in range(size[2])] for j in range(size[1])] for k in range(size[0])]

        self.map_line = [[] for i in range(len(self.net))]

        for gate in gatelist:
            self.grid[0][gate[0]][gate[1]] = -1
        # list of the gates' coordinates
        self.gate = gatelist

    def plot(self):
        # visualization
        data = []
        # gates
        i = 1
        for g in self.gate:
            gate = go.Scatter3d(
                x=[g[0]],
                y=[g[1]],
                z=[0],
                mode="markers+text",
                marker=dict(size=8, color='#000000'),
                text=[str(i)],
                name='G' + str(i)
            )
            i += 1
            data.append(gate)

        # wires
        wires = self.output_line()
        i = 1
        for w in wires:
            wire = go.Scatter3d(
                x=w[0],
                y=w[1],
                z=w[2],
                mode="markers+lines",
                marker=dict(size=3),
                name='W' + str(i)
            )
            i += 1
            data.append(wire)

        # layout
        layout = dict(
            # width=800,
            # height=700,
            # autosize=False,
            title='chip (cost: ' + str(self.cost()) + ')',
            scene=dict(
                xaxis=dict(
                    gridcolor='rgb(255, 255, 255)',
                    zerolinecolor='rgb(255, 255, 255)',
                    showbackground=True,
                    backgroundcolor='rgb(230, 230,230)',
                    range=(0, self.size[1]),
                    dtick=1
                ),
                yaxis=dict(
                    gridcolor='rgb(255, 255, 255)',
                    zerolinecolor='rgb(255, 255, 255)',
                    showbackground=True,
                    backgroundcolor='rgb(230, 230,230)',
                    range=(0, self.size[2]),
                    dtick=1
                ),
                zaxis=dict(
                    gridcolor='rgb(255, 255, 255)',
                    zerolinecolor='rgb(255, 255, 255)',
                    showbackground=True,
                    backgroundcolor='rgb(230, 230,230)',
                    range=(0, self.size[0]),
                    dtick=1
                ),
                camera=dict(
                    up=dict(
                        x=0,
                        y=0,
                        z=1
                    ),
                    eye=dict(
                        x=-1.7428,
                        y=1.0707,
                        z=0.7100,
                    )
                ),
                aspectratio=dict(x=1, y=1, z=0.7),
                aspectmode='manual'
            ),
        )

        # figure
        fig = go.Figure(data=data, layout=layout)
        # plot figure
        py.plot(fig, filename='chip-3d', validate=False)

    def output_map(self, f):
        # for debug
        for i in range(2):
            print("nn", file=f, end=" ")
            for k in range(self.size[2]):
                print("%02d" % k, file=f, end=" ")
            print(file=f)

            for j in range(self.size[1]):
                print("%02d" % j, file=f, end=" ")
                for k in range(self.size[2]):
                    if self.used_wired[i][j][k] >= 0:
                        print("%02d" % self.used_wired[i][j][k], file=f, end=" ")
                    else:
                        print(self.used_wired[i][j][k], file=f, end=" ")
                print(file=f)

            print(file=f)

    def output_line(self):
        # get the ordered coordinates of all the wires
        # for visualization
        line_list = []

        for i in range(len(self.net)):
            line_x = []
            line_y = []
            line_z = []

            for cor in self.map_line[i]:
                line_z.append(cor[0])
                line_x.append(cor[1])
                line_y.append(cor[2])

            line_list.append([line_x, line_y, line_z])

        return line_list

    def addline(self, net_num):
        # add a line

        st = self.net[net_num][0]
        en = self.net[net_num][1]

        queue = []
        # tuple with 4 elements(level, x, y, cost, last) presents level, x-axis, y-axis and last point
        left = 0
        right = 1
        queue.append([0, self.gate[st][0], self.gate[st][1], -1])

        visit = [[[0 for i in range(self.size[2])] for j in range(self.size[1])] for k in range(self.size[0])]

        for i in range(self.size[0]):
            for j in range(self.size[1]):
                for k in range(self.size[2]):
                    visit[i][j][k] = 0

        for i in range(len(self.gate)):
            visit[0][self.gate[i][0]][self.gate[i][1]] = 1
            self.used_wired[0][self.gate[i][0]][self.gate[i][1]] = -1
        visit[0][self.gate[en][0]][self.gate[en][1]] = 0

        while left < right:
            u = queue[left]
            if u[0] == 0 and u[1] == self.gate[en][0] and u[2] == self.gate[en][1]:
                current_cost = 0
                tmp = u[3]
                self.map_line[net_num].append([u[0], u[1], u[2]])
                while tmp != -1:
                    if self.grid[queue[tmp][0]][queue[tmp][1]][queue[tmp][2]] != -1:
                        self.used_wired[queue[tmp][0]][queue[tmp][1]][queue[tmp][2]] = net_num
                        self.map_line[net_num].append([queue[tmp][0], queue[tmp][1], queue[tmp][2]])
                    current_cost = current_cost + 1
                    tmp = queue[tmp][3]
                self.map_line[net_num].append([0, self.gate[st][0], self.gate[st][1]])

                return current_cost

            # up level
            if u[0] < 6:
                if visit[u[0] + 1][u[1]][u[2]] == 0 and self.used_wired[u[0] + 1][u[1]][u[2]] == -1:
                    queue.append([u[0] + 1, u[1], u[2], left])
                    visit[u[0] + 1][u[1]][u[2]] = 1
                    right = right + 1

            # 4 directions in same level
            for i in range(4):
                tx = u[1] + four_direction[i][0]
                ty = u[2] + four_direction[i][1]
                if tx < 0 or tx >= self.size[1] or ty < 0 or ty >= self.size[2]:
                    continue

                if visit[u[0]][tx][ty] == 0 and self.used_wired[u[0]][tx][ty] == -1:
                    queue.append([u[0], tx, ty, left])
                    visit[u[0]][tx][ty] = 1
                    right = right + 1

            # down level
            if u[0] > 0:
                if visit[u[0] - 1][u[1]][u[2]] == 0 and self.used_wired[u[0] - 1][u[1]][u[2]] == -1:
                    queue.append([u[0] - 1, u[1], u[2], left])
                    visit[u[0] - 1][u[1]][u[2]] = 1
                    right = right + 1

            left = left + 1
        return -1

    def delline(self, lab_number):
        # delete a line

        for i in range(self.size[0]):
            for j in range(self.size[1]):
                for k in range(self.size[2]):
                    if self.used_wired[i][j][k] == lab_number:
                        self.used_wired[i][j][k] = -1

        self.map_line[lab_number] = []

    def del_and_add(self, delline_num, addline_num):
        # find a solution, return 0
        # else return 1

        if delline_num == -1:
            # do not need to delete anything
            return 1

        self.delline(delline_num)
        cost1 = self.addline(addline_num)
        cost2 = self.addline(delline_num)
        if cost1 == -1 or cost2 == -1:
            # cannot find a replaced solution

            # back to last status
            if cost1 != -1:
                self.delline(addline_num)
            if cost2 != -1:
                self.delline(delline_num)
            self.addline(delline_num)
            return 1
        else:
            return 0

    def cost(self):
        sum = 0
        for wire in self.map_line:
            sum += len(wire) - 1
        return sum

