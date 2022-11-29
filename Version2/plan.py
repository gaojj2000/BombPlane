# _*_ coding:utf-8 _*_
# FileName: plan.py
# IDE: PyCharm

from enum import Enum
from copy import deepcopy
from typing import List, Tuple


class Direction(Enum):  # 根据飞机朝向定义飞机参数
    UP: List[List[bool]] = [
        [False, False, True, False, False],
        [True, True, True, True, True],
        [False, False, True, False, False],
        [False, True, True, True, False],
    ]
    RIGHT: List[List[bool]] = [
        [False, False, True, False],
        [True, False, True, False],
        [True, True, True, True],
        [True, False, True, False],
        [False, False, True, False],
    ]
    DOWN: List[List[bool]] = [
        [False, True, True, True, False],
        [False, False, True, False, False],
        [True, True, True, True, True],
        [False, False, True, False, False],
    ]
    LEFT: List[List[bool]] = [
        [False, True, False, False],
        [False, True, False, True],
        [True, True, True, True],
        [False, True, False, True],
        [False, True, False, False],
    ]
    UP_DETAIL: List[List[int]] = [
        [0, 0, 1, 0, 0],
        [1, 1, 2, 1, 1],
        [0, 0, 1, 0, 0],
        [0, 1, 1, 1, 0],
    ]
    RIGHT_DETAIL: List[List[int]] = [
        [0, 0, 1, 0],
        [1, 0, 1, 0],
        [1, 1, 2, 1],
        [1, 0, 1, 0],
        [0, 0, 1, 0],
    ]
    DOWN_DETAIL: List[List[int]] = [
        [0, 1, 1, 1, 0],
        [0, 0, 1, 0, 0],
        [1, 1, 2, 1, 1],
        [0, 0, 1, 0, 0],
    ]
    LEFT_DETAIL: List[List[int]] = [
        [0, 1, 0, 0],
        [0, 1, 0, 1],
        [1, 2, 1, 1],
        [0, 1, 0, 1],
        [0, 1, 0, 0],
    ]
    UP_CORE: Tuple[int] = (3, 2)
    RIGHT_CORE: Tuple[int] = (3, 3)
    DOWN_CORE: Tuple[int] = (3, 3)
    LEFT_CORE: Tuple[int] = (2, 3)
    UP_RANGE: List[Tuple[int]] = [(3, 2), (-2, -2)]
    RIGHT_RANGE: List[Tuple[int]] = [(3, 3), (-1, -2)]
    DOWN_RANGE: List[Tuple[int]] = [(3, 3), (-2, -1)]
    LEFT_RANGE: List[Tuple[int]] = [(2, 3), (-2, -2)]


class CssSelector(Enum):
    CORE: str = 'plan_items_core'  # 飞机核心 2
    PLANE: str = 'plan_items'  # 飞机背景 1
    GROUND: str = 'plan_ground'  # 环境背景 0


class_get = {0: CssSelector.GROUND, 1: CssSelector.PLANE, 2: CssSelector.CORE}


class Plan:
    def __init__(self):
        self.__plan1 = deepcopy(Direction(Direction.UP_DETAIL).value)
        self.__plan2 = deepcopy(Direction(Direction.UP_DETAIL).value)
        self.__plan3 = deepcopy(Direction(Direction.UP_DETAIL).value)

    def set_direction(self, plan: str):
        if self.get_direction(plan) == 'UP':
            self[plan] = 'RIGHT_DETAIL'
        elif self.get_direction(plan) == 'RIGHT':
            self[plan] = 'DOWN_DETAIL'
        elif self.get_direction(plan) == 'DOWN':
            self[plan] = 'LEFT_DETAIL'
        elif self.get_direction(plan) == 'LEFT':
            self[plan] = 'UP_DETAIL'

    def get_plan(self, plan: str) -> str:  # 从飞机名称获取飞机对象并转化成html代码
        divs = []
        for row in self[plan]:
            for col in row:
                divs.append(f'<div class="{CssSelector(class_get[col]).value}">{plan if col == 2 else ""}</div>')
        return ''.join(divs)

    def get_direction(self, plan: str):
        return Direction([list(map(bool, l)) for l in self[plan]]).name

    def get_core(self, plan: str = None, direction: str = None):
        if direction:
            return Direction[f'{direction}_CORE'].value
        elif plan:
            return Direction[f'{self.get_direction(plan)}_CORE'].value
        else:
            return Direction[f'{self.get_direction("plan1")}_CORE'].value

    def get_range(self, plan: str = None, direction: str = None):
        if direction:
            return Direction[f'{direction}_RANGE'].value
        elif plan:
            return Direction[f'{self.get_direction(plan)}_RANGE'].value
        else:
            return Direction[f'{self.get_direction("plan1")}_RANGE'].value

    def __getitem__(self, item: str):
        return self.__dict__[f'_Plan__{item}']

    def __setitem__(self, key: str, value: str):
        self.__dict__[f'_Plan__{key}'] = deepcopy(Direction[value].value)
