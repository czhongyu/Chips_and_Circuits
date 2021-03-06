import random
import sys
sys.path.append('../')
from classes.chip import Chip


class AstarSpfa:
    """
        This is the method to find path in the chip.
        Use the algorithm called SPFA.
        Once the user wants a simpler algorithm Breadth-First-Search to implement,
            just sets the variable 'use_spfa' as 0.
    """

    def __init__(self, environment):
        self.env = environment
        self.chip = Chip(self.env)

    def calc_per_pairgate(self, flag_conflict, pair, cnt):
        if flag_conflict == 1:
            for i in range(4):
                if flag_conflict == 0:
                    break
                tx = self.chip.gate[pair][0] + self.env.four_direction[i][0]
                ty = self.chip.gate[pair][1] + self.env.four_direction[i][1]

                if tx < 0 or tx >= self.chip.size[1] or ty < 0 or ty >= self.chip.size[2]:
                    continue

                net_num = self.chip.used_wired[0][tx][ty]

                flag_conflict = self.chip.del_and_add(net_num, cnt)

        if flag_conflict == 1:
            net_num = self.chip.used_wired[1][self.chip.gate[pair][0]][self.chip.gate[pair][1]]
            flag_conflict = self.chip.del_and_add(net_num, cnt)

        return flag_conflict

    def astar_spfa(self):
        cnt = 0
        for pair_gate in self.chip.net:
            cost = self.chip.addline(cnt)
            flag_conflict = 0
            # If there is a conflict occurs, the 'flag_conflict' will be 1.

            if cost == -1:

                flag_conflict = 1

                flag_conflict = self.calc_per_pairgate(flag_conflict, pair_gate[0], cnt)

                flag_conflict = self.calc_per_pairgate(flag_conflict, pair_gate[1], cnt)

            if flag_conflict == 0:
                cnt = cnt + 1
            else:
                return cnt

        return cnt

    def run_until_solution(self, if_plot=0):
        total_wires = len(self.chip.net)
        answer = 0
        while answer != total_wires:
            self.chip.clean()
            random.shuffle(self.chip.net)
            answer = self.astar_spfa()
            print("The number of connected wires / total wires =", answer, '/', total_wires)

        print("find a solution")

        if if_plot:
            self.chip.plot("test")

        return answer

    def run(self, complete, use_spfa=1):
        if not use_spfa:
            # Change the situation to the more simple algorithm - Breadth-First-Search.
            self.chip.grid_value = self.chip.memset_list(1)

        random.shuffle(self.chip.net)

        if complete:
            self.run_until_solution(1)
        else:
            print("The number of connected wires / total wires =", self.astar_spfa(), '/', len(self.chip.net))
            self.chip.plot("test")

        if not use_spfa:
            # Recover the grid_value to initial values.
            self.chip.manhattan_distance_weight()

    def wrapper(self, chip_input, valid=False):
        self.chip = chip_input
        if valid:
            return self.run_until_solution()
        else:
            return self.astar_spfa()


