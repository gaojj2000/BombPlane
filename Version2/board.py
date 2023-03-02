# _*_ coding:utf-8 _*_
# Project: 
# FileName: board.py
# UserName: 高俊佶
# ComputerUser：19305
# Day: 2021/12/9
# Time: 12:00
# IDE: PyCharm
# 女人，不要也罢！——来自2021-10-9日的灵魂伤感

from enum import Enum
from plan import Plan


class Color(Enum):
    PLANE: str = '#25a0e4'  # 飞机背景 1
    GROUND: str = 'rgba(37, 160, 228, 0.4)'  # 环境背景 0
    ATTACK: str = 'red'  # 击中飞机机身 -1
    MISS: str = 'white'  # 未击中 -2
    CRASH: str = 'gray'  # 坠毁（击中飞机核心）-3


color_get = {-3: Color.CRASH, -2: Color.MISS, -1: Color.ATTACK, 0: Color.GROUND, 1: Color.PLANE}


class CssSelector(Enum):
    CORE: str = 'core'  # 飞机核心 2
    PLANE: str = 'plane'  # 飞机背景 1
    GROUND: str = 'ground'  # 环境背景 0
    ATTACK: str = 'attack'  # 击中飞机机身 -1
    MISS: str = 'miss'  # 未击中 -2
    CRASH: str = 'crash'  # 坠毁（击中飞机核心）-3


class_get = {-3: CssSelector.CRASH, -2: CssSelector.MISS, -1: CssSelector.ATTACK, 0: CssSelector.GROUND, 1: CssSelector.PLANE, 2: CssSelector.CORE}


class Board(Plan):

    LEFT = 'l_'
    RIGHT = 'r_'

    def __init__(self, size: int = 12):
        super().__init__()
        self.first = False  # 是否先手
        self.attachable = False  # 是否轮到攻击
        self.__size = 12  # 默认大小为 12
        if isinstance(size, int) and 10 <= size <= 20:
            self.__size = size
        self.plan_core = {'plan1': None, 'plan2': None, 'plan3': None}  # 保存飞机核心
        self.plan_alive = {'plan1': True, 'plan2': True, 'plan3': True}  # 飞机存活情况，方便决定胜负
        self.__board = [[0 for _ in range(self.__size)] for _ in range(self.__size)]  # 生成初始棋盘

    def judge_plan(self, plan: str, x: int, y: int):  # 使用实际坐标，内部使用索引要减一
        plan_range = self.get_range(plan)
        if x < plan_range[0][0] or y < plan_range[0][1] or x > self.__size + plan_range[1][0] or y > self.__size + plan_range[1][1]:
            return '飞机不能超出边界哦！'
        for row in range(y - plan_range[0][1], y - plan_range[1][1]):
            for col in range(x - plan_range[0][0], x - plan_range[1][0]):
                if self.__board[row][col] and self[plan][row - y + plan_range[0][1]][col - x + plan_range[0][0]]:
                    return '此处已有其他飞机了！'
        return False

    def draw_plan(self, plan: str, index: int):  # 使用实际坐标，内部使用索引要减一
        x, y = self.index_to_site(index)
        res = self.judge_plan(plan, x, y)
        if res:
            return res
        else:
            plan_range = self.get_range(plan)
            self.plan_core[plan] = (x, y)
            for row in range(y - plan_range[0][1], y - plan_range[1][1]):
                for col in range(x - plan_range[0][0], x - plan_range[1][0]):
                    if not self.__board[row][col]:
                        self.__board[row][col] = self[plan][row - y + plan_range[0][1]][col - x + plan_range[0][0]]

    def check_crash_plan(self, x: int, y: int):  # 检查击中需要坠毁的是哪架飞机 (x, y)【实际坐标】(下标坐标各自加一)
        for plan in self.plan_core:
            if self.plan_core[plan] == (x, y):
                return plan

    def crash(self, plan: str):  # 击中飞机核心导致坠毁
        self.plan_alive[plan] = False
        if self.plan_core[plan]:
            x, y = self.plan_core[plan]
            plan_range = self.get_range(plan)
            for row in range(y - plan_range[0][1], y - plan_range[1][1]):
                for col in range(x - plan_range[0][0], x - plan_range[1][0]):
                    if self[plan][row - y + plan_range[0][1]][col - x + plan_range[0][0]]:
                        self.__board[row][col] = -3
        return False

    def attack(self, site: int):  # 攻击飞机（当前对象是对方）
        self.attachable = True
        x, y = self.index_to_site(site)
        num = self.__board[y - 1][x - 1]
        if num > 0:
            if num == 2:
                self.crash(self.check_crash_plan(x, y))
            elif self.__board[y - 1][x - 1] != -3:
                self.__board[y - 1][x - 1] = -1
        elif not num:
            self.__board[y - 1][x - 1] = -2

    def index_to_site(self, index: int):  # x为横坐标 (第几列)，y为纵坐标 (第几行)，返回 (x, y)【实际坐标】(下标坐标各自加一)
        return index % self.__size + 1, index // self.__size + 1

    def site_to_index(self, x: int, y: int):  # (x, y)【实际坐标】(下标坐标各自加一)
        return (y - 1) * self.__size + x - 1

    # def print_board(self):  # 打印棋盘 0 1 字符（临时）
    #     for row in self.__board:
    #         print(*row, sep='  ')
    #     print()

    def get_board(self, location: str):  # 将棋盘显示转化成html代码
        divs = []
        for nr, row in enumerate(self.__board):
            for nc, col in enumerate(row):
                if location == self.LEFT:
                    if col == 2:
                        for plan in self.plan_core:
                            if self.plan_core[plan] == (nc + 1, nr + 1):
                                divs.append(f'<div id="{location}{len(divs)}" class="{CssSelector(class_get[col]).value}">{plan}</div>')
                    else:
                        divs.append(f'<div id="{location}{len(divs)}" class="{CssSelector(class_get[col]).value}"></div>')
                elif location == self.RIGHT:
                    if col > 0:
                        col = 0
                    divs.append(f'<div id="{location}{len(divs)}" class="{CssSelector(class_get[col]).value}" onclick="attack(this)"></div>')
        return ''.join(divs)
