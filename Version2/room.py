# _*_ coding:utf-8 _*_
# FileName: room.py
# IDE: PyCharm

from enum import Enum
from board import Board


class CssSize:
    def __init__(self, size: int):
        self.size = size  # 10、12、15、20
        self.border = 600
        self.item = self.border // self.size  # 60、50、40、30
        self.font_size = self.item // 10 * 3


class CssSizeDict(Enum):
    SIZE10: CssSize = CssSize(size=10)
    SIZE12: CssSize = CssSize(size=12)
    SIZE15: CssSize = CssSize(size=15)
    SIZE20: CssSize = CssSize(size=20)


class Room:
    def __init__(self, room: int, size: int):
        assert isinstance(room, int) and len(str(room)) == 4
        self.size = size
        self.boards = {}
        self.room = room

    def set_first(self, first: str):
        assert first in ['0', '1']
        if first == '0':
            self.boards['0'].first = True
            self.boards['1'].first = False
        else:
            self.boards['1'].first = True
            self.boards['0'].first = False

    def make_item_size(self, user):  # 按棋盘大小生成每个小格的大小属性
        try:
            css = CssSizeDict[f'SIZE{self.size}'].value
        except KeyError:
            css = CssSizeDict(CssSizeDict.SIZE12).value
        style = f"""
            .ground, .plane, .attack, .miss, .crash {{
                width: {css.item}px;
                height: {css.item}px;
            }}
            
            .core {{
                text-align: center;
                font-size: {css.font_size}px;
                width: {css.item - 2}px;
                height: {css.item - 2}px;
                line-height: {css.item - 2}px;
            }}
        """
        for plan in ['plan1', 'plan2', 'plan3']:
            if self.boards[user].get_direction(plan) in ['RIGHT', 'LEFT']:
                style += f"""
                
            #{plan} {{
                width: 202px;
                height: 252px;
            }}
                """
            else:
                style += f"""
                
            #{plan} {{
                width: 252px;
                height: 202px;
            }}
                """
        return style
