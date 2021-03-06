import io
from collections import deque
import time
import logging

import sys


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def current_ms():
    return time.time() * 1000


tick = 0
robot = None
orders = []
orders_map = dict()
total_time_took_ms = 0

stop_сommand = ""
for i in range(60):
    stop_сommand += "S"
stop_сommand += "\n"


class Robot:
    def __init__(self, loc):
        self.loc = loc
        self.goods = False
        self.order = None
        self.path = None
        self.target = None
        self.commandline = []
        self.output = []

    def find_path(self, orders):

        # start_time = time.time() * 1000.0

        if not self.goods:
            orders_starts = [order.start for order in orders]
            # print('orders_starts:', orders_starts)
            if not orders_starts:
                self.path = None
                return
            search_result = breath_first_search(grid, self.loc, orders_starts)
            # print('search res', search_result)
            self.order = orders_map[search_result[1]][0]
            # print('self_ordrr', self.order.start)
            self.target = self.order.start
            self.path = get_path(search_result[0], self.loc, self.target)
            # print('selfpath', self.path)
            return
        self.target = self.order.end
        # print('orderEND', self.order.end)
        search_result = breath_first_search(grid, self.loc, [self.target])
        # print('search_result!!!', search_result)
        self.path = get_path(search_result[0], self.loc, self.target)
        # print('SELFPATH', self.path)
        return

    def walk(self):
        start_time = time.time() * 1000.0
        global orders, orders_map
        try:
            char = self.commandline.pop(0)
            if char == "L":
                self.loc = (self.loc[0] - 1, self.loc[1])
            elif char == "R":
                self.loc = (self.loc[0] + 1, self.loc[1])
            elif char == "U":
                self.loc = (self.loc[0], self.loc[1] - 1)
            elif char == "D":
                self.loc = (self.loc[0], self.loc[1] + 1)
            elif char == 'T':
                orders_map[self.loc].pop(0)
            elif char == 'P':
                pass
            elif char == 'S':
                pass
            self.output.append(char)
        except IndexError:
            self.goods = not self.goods
            if self.target == self.order.end and orders:
                try:
                    index = orders.index(self.order)
                    orders.pop(index)
                except:
                    pass
            if orders:
                self.find_path(orders)
                self.create_commandline()
                return
            self.path = None

        end_time = time.time() * 1000.0
        logging.info('robot walk time: %d', end_time - start_time)

    def create_commandline(self):
        if not self.path:
            return
        for i in range(len(self.path)):
            if self.path[i] == self.path[-1]:
                if self.goods:
                    self.commandline.append('P')
                else:
                    self.commandline.append('T')
                continue
            shift_x = self.path[i + 1][0] - self.path[i][0]
            shift_y = self.path[i + 1][1] - self.path[i][1]
            shift = (shift_x, shift_y)
            if shift == (0, 1):
                self.commandline.append('D')
            elif shift == (0, -1):
                self.commandline.append('U')
            elif shift == (1, 0):
                self.commandline.append('R')
            elif shift == (-1, 0):
                self.commandline.append('L')


class Order(object):
    def __init__(self, start, end, created_at):
        self.start = start
        self.end = end
        self.created_at = created_at


class Grid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.barriers = []

    def in_bounds(self, point):
        (x, y) = point
        return 0 <= x < self.width and 0 <= y < self.height

    def is_not_barrier(self, point):
        # TODO use plain arrays
        return not self.barriers[point[1]][point[0]]
        #  return point not in self.barriers  # TODO OPTIMIZE - SLOW PART

    def get_neighbors(self, point):
        start_time = time.time() * 1000.0
        (x, y) = point
        # East, West, North, South
        neighbors = [(x + 1, y), (x - 1, y), (x, y - 1), (x, y + 1)]
        # South, North, West, East
        if (x + y) % 2 == 0:
            neighbors.reverse()
        results = filter(self.in_bounds, neighbors)
        results = filter(self.is_not_barrier, results)
        end_time = time.time() * 1000.0
        return results


class Queue:
    def __init__(self):
        self.queue = deque()

    def get_next_point(self):
        return self.queue.popleft()

    def put(self, point):
        self.queue.append(point)

    def is_empty(self):
        return not self.queue


def breath_first_search(graph, start_point, finish_points: list = []):
    start_time = time.time() * 1000.0
    frontier = Queue()
    frontier.put(start_point)
    came_from = dict()
    came_from[start_point] = None
    target_point = None

    while not frontier.is_empty():
        current_point = frontier.get_next_point()

        if current_point in finish_points:
            target_point = current_point
            break

        for next_point in graph.get_neighbors(current_point):
            if next_point not in came_from:
                frontier.put(next_point)
                came_from[next_point] = current_point
    end_time = time.time() * 1000.0
    logging.info('breath_first_search time: %d', end_time - start_time)
    return came_from, target_point


# start must be the same that was in breath_first_search
def get_path(came_from, start_point, finish_point):
    start_time = time.time() * 1000.0
    current_point = finish_point
    path = []

    while current_point != start_point:
        path.append(current_point)
        # if not came_from.__contains__(current_point):
        #     eprint("failed to get path <<< path:")
        #     eprint(path)
        #     eprint("came_from.size =")
        #     eprint(came_from)
        #
        current_point = came_from[current_point]
    path.append(start_point)
    path.reverse()
    end_time = time.time() * 1000.0
    return path


def main():
    global barriers, robot, grid, total_time_took_ms, tick, orders, orders_map
    f = io.open(sys.stdin.fileno())
    first_str = f.readline().split(' ')
    N = int(first_str[0])
    max_tips = int(first_str[1])
    cost = int(first_str[2])
    map_ = f.readlines(N * N)

    barriers = []  # y x

    def add_barriers(map_):
        for y, line in enumerate(map_):
            barriers.append([])
            for x, point in enumerate(line):
                barriers[y].append(point == '#')

    add_barriers(map_)

    second_str = f.readline().split(' ')

    n_iters = int(second_str[0])
    n_orders = int(second_str[1])

    sys.stdout.write(str(1) + '\n')
    for x in range(N):
        for y in range(N):
            if barriers[y][x] == False and robot is None:
                robot = Robot((x, y))
                sys.stdout.write(f'{y + 1} {x + 1}\n')
                sys.stdout.flush()

    def get_orders(file):
        n_orders_str = file.readline()
        if (n_orders_str == ""):
            n_orders_str = file.readline()

        n_orders = int(n_orders_str)
        new_orders = []
        for i in range(n_orders):
            order = file.readline().split()
            new_orders.append(order)
        return new_orders

    def add_orders(new_orders):
        global orders, tick, orders_map
        for order_str in new_orders:
            order = Order((int(order_str[1]) - 1, int(order_str[0]) - 1),
                          (int(order_str[3]) - 1, int(order_str[2]) - 1), tick)
            orders.append(order)
            if not order.start in orders_map:
                orders_map[order.start] = []
            orders_map[order.start].append(order)
            # eprint(
            #    "Order start = " + str(order.start[0]) + " " + str(order.start[1]) +
            #    " Order end = " + str(order.end[0]) + " " + str(order.end[1]))

    grid = Grid(N, N)
    grid.barriers = barriers

    for i in range(n_iters):
        new_orders = get_orders(f)

        if total_time_took_ms > 16500:
            sys.stdout.write(stop_сommand)
            sys.stdout.flush()
            continue
        f.flush()

        start_ms = current_ms()

        if new_orders:
            add_orders(new_orders)

        orders = list(filter(lambda o: tick - o.created_at < max_tips, orders))

        if not robot.path and orders:
            candidates = list(filter(lambda o: orders_map[o.start][0] == o, orders))
            robot.find_path(candidates)
            robot.create_commandline()
        k = 0
        while k < 60 and robot.path:
            robot.walk()
            k += 1

        if len(robot.output) < 60:
            robot.output.extend(['S' for x in range(60 - len(robot.output))])

        sys.stdout.write(''.join(robot.output) + '\n')
        sys.stdout.flush()
        robot.output = []

        end_ms = current_ms()

        took_ms = end_ms - start_ms
        total_time_took_ms = total_time_took_ms + (took_ms)
        tick += 60


import traceback

try:
    main()
except BaseException as e:
    tb = traceback.format_exc()
    print(tb)
    print(e)
