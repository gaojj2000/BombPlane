# _*_ coding:utf-8 _*_
# FileName: main.py
# IDE: PyCharm

# ps -aux | grep -v grep | grep python3
# nohup /www/server/panel/pyenv/bin/python3.7 main.py > flask.log 2>&1 &
# 110.42.181.215:8866
# cat /dev/null > ~/.bash_history && history -c && exit

# nohup python3 main.py > flask.log 2>&1 &
# ps -aux | grep -v grep | grep python3
# for pid in `ps -aux | grep -v grep | grep python3 | awk '{print $2}'`;do kill -9 $pid;done
# cat /dev/null > ~/.bash_history && history -c && exit

"""
炸飞机双人小游戏在线玩：
元素：房间、棋盘、飞机
每个房间内有两个棋盘
每个棋盘上有三架飞机
棋盘(飞机) -> 房间(棋盘)
"""

from time import sleep
from room import Room, Board
from flask_cors import CORS
from flask import Flask, request, make_response, render_template, jsonify

rooms = {}
app = Flask(import_name=__name__, static_folder='templates/static', template_folder='templates')
app.config.from_object(__name__)
CORS(app, origins='*', supports_credentials=True)

login_html = """
				<form id="play" method="get" action="/">
					<p id="room"><input type="text" name="room" placeholder="请输入房间号（4位数字）" /></p>
					<p id="res">
						<span>大小：</span>
						<select name="size">
							<option value="10">10</option>
							<option value="12">12</option>
							<option value="15">15</option>
							<option value="20">20</option>
						</select>
						<input type="submit" value="加入" />
					</p>
				</form>
"""


def people_wait(room: str):
    """
    等待对手就绪
    :param room: 房间号
    :return:
    """
    while 1:
        if room in rooms and rooms[room].boards.get('1', None):
            return True
        sleep(0.5)


def start_wait(room: str):
    """
    等待双方飞机放置完毕并确定先后手
    :param room:
    :return:
    """
    while 1:
        if None not in list(rooms[room].boards['0'].plan_core.values()) and None in list(rooms[room].boards['1'].plan_core.values()):
            rooms[room].set_first('0')
        elif None in list(rooms[room].boards['0'].plan_core.values()) and None not in list(rooms[room].boards['1'].plan_core.values()):
            rooms[room].set_first('1')
        elif None not in list(rooms[room].boards['0'].plan_core.values()) and None not in list(rooms[room].boards['1'].plan_core.values()):
            return True
        sleep(0.5)


def player_wait(room: str, user: str):
    """
    等待对手就绪
    :param room: 房间号
    :param user: 用户序号
    :return:
    """
    while 1:
        if room in rooms and rooms[room].boards[user].attachable:
            return True
        sleep(0.5)


@app.route('/', methods=['GET'])
def index():
    """
    各种情况：
        没有房间号且首次创建房间 -> 创建所有元素
        没有房间号且加入房间 -> 创建所有元素
        有房间号 ->  创建所有元素
        异常（房间号不正确、人数已满） -> 不传递元素
    :return:
    """
    if not request.cookies.get('room'):  # 未加入房间的玩家
        room_ = request.args.get('room')  # 获取表单给予的数据
        size = request.args.get('size')  # 获取表单给予的数据
        if room_ and size:
            try:
                if room_ not in rooms:
                    rooms[room_] = Room(int(room_), int(size))
                elif (rooms[room_].boards.get('0') and rooms[room_].boards['0'].attachable) and (rooms[room_].boards.get('1') and rooms[room_].boards['1'].attachable):
                    rooms[room_] = Room(int(room_), int(size))
                room = rooms[room_]
                if not room.boards.get('0', None):  # 第一位加入房间（创建房间）的人
                    room.boards['0'] = Board(size=room.size)
                    temple = render_template('index.html', left=room.boards['0'].get_board(Board.LEFT), right=room.boards['0'].get_board(Board.LEFT),
                                             plan1=room.boards['0'].get_plan('plan1'), plan2=room.boards['0'].get_plan('plan2'), plan3=room.boards['0'].get_plan('plan3'),
                                             size_style=room.make_item_size('0'), msg='等待对方进入房间', onload="ajax('/wait_two_people', refreash);",
                                             login_html=f'<p>当前房间号：{room.room}</p><p><button onclick="logout()">退出房间</button></p>')
                    res = make_response(temple, 200)
                    res.set_cookie('user', '0', max_age=21600)  # 默认登录6个小时
                elif not room.boards.get('1', None):  # 第二位加入房间的人
                    room.boards['1'] = Board(size=room.size)
                    temple = render_template('index.html', left=room.boards['1'].get_board(Board.LEFT), right=room.boards['0'].get_board(Board.RIGHT),
                                             plan1=room.boards['1'].get_plan('plan1'), plan2=room.boards['1'].get_plan('plan2'), plan3=room.boards['1'].get_plan('plan3'),
                                             size_style=room.make_item_size('1'), show='display: none;')
                    res = make_response(temple, 200)
                    res.set_cookie('user', '1', max_age=21600)  # 默认登录6个小时
                else:  # 在房间人数已满的情况下想加入房间的人
                    return make_response(render_template('index.html', msg='该房间人员已满！', login_html=login_html), 400)
                res.set_cookie('room', room_, max_age=21600)  # 默认登录6个小时
            except AssertionError:  # 通过内部错误上抛来判断房间号输入不符合规则
                res = make_response(render_template('index.html', msg='房间号错误请重新输入', login_html=login_html), 200)
        else:
            res = make_response(render_template('index.html', msg='请输入房间号开始游戏', login_html=login_html), 200)
    else:  # 已经加入房间的玩家
        room = rooms[request.cookies.get('room')]
        user = request.cookies.get('user')
        if room.boards.get('1', None):  # 已经开局
            plan_dict = dict(plan1=room.boards[user].get_plan('plan1'), plan2=room.boards[user].get_plan('plan2'), plan3=room.boards[user].get_plan('plan3'))
            # 去除已经放置的飞机模型
            for plan in room.boards[user].plan_core:
                if room.boards[user].plan_core[plan]:
                    del plan_dict[plan]
            # 当三架飞机已经摆放完毕，去除已经放置的飞机模型外框
            if not plan_dict:
                plan_dict['ok'] = 'display: none;'
                plan_dict['onload'] = "ajax('/wait_start', refreash);"
                if None not in list(room.boards['0'].plan_core.values()) and None not in list(room.boards['1'].plan_core.values()):
                    if not room.boards[user].attachable:
                        plan_dict['onload'] = "ajax('/wait_player', refreash);"
                    else:
                        del plan_dict['onload']
            if set(room.boards[user].plan_alive.values()) == {False}:
                temple = render_template('index.html', left=room.boards[user].get_board(Board.LEFT), right=room.boards['0' if int(user) else '1'].get_board(Board.RIGHT),
                                         size_style=room.make_item_size(user), msg='你输了！重新开始？', ok='display: none;', login_html=login_html)
                res = make_response(temple, 200)
                res.delete_cookie('room')
                res.delete_cookie('user')
                room.boards[user].attachable = True
                room.boards['0' if int(user) else '1'].attachable = True
                return res
            elif set(room.boards['0' if int(user) else '1'].plan_alive.values()) == {False}:
                temple = render_template('index.html', left=room.boards[user].get_board(Board.LEFT), right=room.boards['0' if int(user) else '1'].get_board(Board.RIGHT),
                                         size_style=room.make_item_size(user), msg='你赢了！重新开始？', ok='display: none;', login_html=login_html)
                res = make_response(temple, 200)
                res.delete_cookie('room')
                res.delete_cookie('user')
                room.boards[user].attachable = True
                room.boards['0' if int(user) else '1'].attachable = True
                return res
            else:
                temple = render_template('index.html', left=room.boards[user].get_board(Board.LEFT), right=room.boards['0' if int(user) else '1'].get_board(Board.RIGHT),
                                         size_style=room.make_item_size(user), show='display: none;', **plan_dict)
        else:  # 对方暂时没有进入房间
            temple = render_template('index.html', left=room.boards[user].get_board(Board.LEFT), right=room.boards['0' if int(user) else '1'].get_board(Board.RIGHT),
                                     plan1=room.boards[user].get_plan('plan1'), plan2=room.boards[user].get_plan('plan2'), plan3=room.boards[user].get_plan('plan3'),
                                     size_style=room.make_item_size(user), msg='等待对方进入房间', login_html=f'<p>当前房间号：{room.room}</p><p><button onclick="logout()">退出房间</button></p>')
        res = make_response(temple, 200)
    return res


@app.route('/wait_two_people', methods=['GET'])  # 学会协程后尝试异步
def wait_two_people():
    """
    判断是否双人进入房间：
    :return:
    """
    if not request.cookies.get('room'):
        return make_response(render_template('index.html', msg='请输入房间号开始游戏'), 200)
    elif people_wait(request.cookies.get('room')):
        return make_response(jsonify({'code': 0, 'msg': '对方已就绪！'}), 200)


@app.route('/wait_start', methods=['GET'])  # 学会协程后尝试异步
def wait_start():
    """
    等待双方摆好飞机并确定先手
    :return:
    """
    if not request.cookies.get('room'):
        return make_response(render_template('index.html', msg='请输入房间号开始游戏'), 200)
    elif start_wait(request.cookies.get('room')):
        room = rooms[request.cookies.get('room')]
        user = request.cookies.get('user')
        first = room.boards[user].first
        if first:
            room.boards[user].attachable = True
            temple = render_template('index.html', left=room.boards[user].get_board(Board.LEFT), right=room.boards['0' if int(user) else '1'].get_board(Board.RIGHT),
                                     size_style=room.make_item_size(user), show='display: none;', ok='display: none;')
        else:
            room.boards[user].attachable = False
            temple = render_template('index.html', left=room.boards[user].get_board(Board.LEFT), right=room.boards['0' if int(user) else '1'].get_board(Board.RIGHT),
                                     size_style=room.make_item_size(user), show='display: none;', ok='display: none;', onload="ajax('/wait_player', refreash);")
        return make_response(temple, 200)


@app.route('/wait_player', methods=['GET'])  # 学会协程后尝试异步
def wait_player():
    """
    等待双方出手并判断游戏是否结束
    :return:
    """
    if not request.cookies.get('room'):
        return make_response(render_template('index.html', msg='请输入房间号开始游戏'), 200)
    elif player_wait(request.cookies.get('room'), request.cookies.get('user')):
        room = rooms[request.cookies.get('room')]
        user = request.cookies.get('user')
        temple = render_template('index.html', left=room.boards[user].get_board(Board.LEFT), right=room.boards['0' if int(user) else '1'].get_board(Board.RIGHT),
                                 size_style=room.make_item_size(user), show='display: none;', ok='display: none;', onload="ajax('/wait_player', refreash);")
        return make_response(temple, 200)


@app.route('/attack', methods=['GET'])
def attack():
    if not request.cookies.get('room'):
        return make_response(render_template('index.html', msg='请输入房间号开始游戏', login_html=login_html), 200)
    room = rooms[request.cookies.get('room')]
    user = request.cookies.get('user')
    site = request.args.get('site')
    attachable = room.boards[user].attachable
    if attachable:
        room.boards[user].attachable = False
        room.boards['0' if int(user) else '1'].attack(int(site))
        temple = render_template('index.html', left=room.boards[user].get_board(Board.LEFT), right=room.boards['0' if int(user) else '1'].get_board(Board.RIGHT),
                                 size_style=room.make_item_size(user), show='display: none;', ok='display: none;')
    else:
        temple = render_template('index.html', left=room.boards[user].get_board(Board.LEFT), right=room.boards['0' if int(user) else '1'].get_board(Board.RIGHT),
                                 size_style=room.make_item_size(user), show='display: none;', ok='display: none;')
    return make_response(temple, 200)


@app.route('/set_direction', methods=['GET'])
def set_direction():
    if not request.cookies.get('room'):
        return make_response(render_template('index.html', msg='请输入房间号开始游戏', login_html=login_html), 200)
    room = rooms[request.cookies.get('room')]
    plan = request.args.get('plan')
    user = request.cookies.get('user')
    if plan:
        room.boards[user].set_direction(plan)
    plan_dict = dict(plan1=room.boards[user].get_plan('plan1'), plan2=room.boards[user].get_plan('plan2'), plan3=room.boards[user].get_plan('plan3'))
    for plan in room.boards[user].plan_core:
        if room.boards[user].plan_core[plan]:
            del plan_dict[plan]
    if not plan_dict:
        plan_dict['ok'] = 'display: none;'
    temple = render_template('index.html', left=room.boards[user].get_board(Board.LEFT), right=room.boards['0' if int(user) else '1'].get_board(Board.RIGHT),
                             size_style=room.make_item_size(user), show='display: none;', **plan_dict)
    return make_response(temple, 200)


@app.route('/draw_plan', methods=['GET'])
def draw_plan():
    if not request.cookies.get('room'):
        return make_response(render_template('index.html', msg='请输入房间号开始游戏', login_html=login_html), 200)
    room = rooms[request.cookies.get('room')]
    plan = request.args.get('plan')
    site = request.args.get('site')
    user = request.cookies.get('user')
    if plan and site:
        room.boards[user].draw_plan(plan, int(site))
    plan_dict = dict(plan1=room.boards[user].get_plan('plan1'), plan2=room.boards[user].get_plan('plan2'), plan3=room.boards[user].get_plan('plan3'))
    for plan in room.boards['0'].plan_core:
        if room.boards['0'].plan_core[plan]:
            del plan_dict[plan]
    if not plan_dict:
        plan_dict['ok'] = 'display: none;'
    temple = render_template('index.html', left=room.boards[user].get_board(Board.LEFT), right=room.boards['0' if int(user) else '1'].get_board(Board.RIGHT),
                             size_style=room.make_item_size(user), show='display: none;', **plan_dict)
    return make_response(temple, 200)


@app.route('/logout', methods=['GET'])
def logout():
    """
    退出房间、清除 cookies
    :return:
    """
    if not request.cookies.get('room'):
        return make_response(render_template('index.html', msg='请输入房间号开始游戏', login_html=login_html), 200)
    del rooms[request.cookies.get('room')].boards[request.cookies.get('user')]
    if not rooms[request.cookies.get('room')].boards:
        del rooms[request.cookies.get('room')]
    res = make_response(jsonify({'code': 0, 'msg': '退出房间成功！'}))
    res.delete_cookie('room')
    res.delete_cookie('user')
    return res


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8866, threaded=True, processes=1)
