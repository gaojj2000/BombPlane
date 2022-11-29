# _*_ coding:utf-8 _*_
# FileName: BombPlane.py
# IDE: PyCharm

# nohup python3 BombPlane.py > flask.log 2>&1 &
# for pid in `ps -aux | grep -v grep | grep python3 | awk '{print $2}'`;do kill -9 $pid;done
# cat /dev/null > ~/.bash_history && history -c && exit

# 炸飞机（网页联机）【通过4位随机数匹配连接】
import time
from time import sleep
from flask_cors import CORS
from flask import Flask, request, make_response, render_template, jsonify

rooms = {}
app = Flask(import_name=__name__, static_folder='html/static', template_folder='html')
app.config.from_object(__name__)
CORS(app, origins='*', supports_credentials=True)


class Plan:
    def __init__(self):
        self.site = {}
        self.fill = [
            [0, 0, 1, 0, 0],
            [1, 1, 1, 1, 1],
            [0, 0, 1, 0, 0],
            [0, 1, 1, 1, 0],
        ]
        self.first = False  # 我方先手
        self.board = []  # 我方飞机区域
        self.attachable = False  # 是否轮到攻击
        self.other = [[0 for _ in range(12)] for _ in range(12)]  # 敌方飞机区域
        self.kills = [0, 0, 0]  # 我方每架飞机是否击毁

    def set_site(self, site: tuple, plan: str):
        self.site.update({plan: site})

    def set_board(self, board: list):
        self.board = board


class Room:
    def __init__(self, room: str):
        self.room = room  # 房间号
        self.plans = []  # 房间飞机区域对象

    def add(self, plan: Plan):
        if len(self.plans) < 2:
            self.plans.append(plan)

    def check_live(self):
        if self.room:
            return True


def wait(room: str):
    while 1:
        if room in rooms and len(rooms[room].plans) == 2:
            return True
        sleep(0.5)


def plan_wait(room: str):
    while 1:
        if len(rooms[room].plans[0].site.keys()) == 3 and len(rooms[room].plans[1].site.keys()) != 3:
            rooms[room].plans[0].first = True
            rooms[room].plans[0].attachable = True
        elif len(rooms[room].plans[0].site.keys()) != 3 and len(rooms[room].plans[1].site.keys()) == 3:
            rooms[room].plans[1].first = True
            rooms[room].plans[1].attachable = True
        elif len(rooms[room].plans[0].site.keys()) == 3 and len(rooms[room].plans[1].site.keys()) == 3:
            return True
        sleep(0.5)


def player_draw(room: str, user: str, x: str, y: str):
    if int(x) > 0 and int(y) > 0:
        rooms[room].plans[0].attachable, rooms[room].plans[1].attachable = rooms[room].plans[1].attachable, rooms[room].plans[0].attachable
        if rooms[room].plans[0 if int(user) else 1].board[int(y) - 1][int(x) - 1]:
            rooms[room].plans[int(user)].other[int(y) - 1][int(x) - 1] = -2
            rooms[room].plans[0 if int(user) else 1].board[int(y) - 1][int(x) - 1] = -2
        else:
            rooms[room].plans[0 if int(user) else 1].board[int(y) - 1][int(x) - 1] = -1
            rooms[room].plans[int(user)].other[int(y) - 1][int(x) - 1] = -1
        for plan, site in rooms[room].plans[0 if int(user) else 1].site.items():
            if (int(x), int(y)) == site:
                rooms[room].plans[0 if int(user) else 1].kills[int(plan[-1]) - 1] = 1
                for row in range(site[1] - 2, site[1] + 2):
                    for col in range(site[0] - 3, site[0] + 2):
                        if rooms[room].plans[0 if int(user) else 1].fill[row - site[1] + 2][col - site[0] + 3]:
                            rooms[room].plans[int(user)].other[row][col] = -3 - int(plan[-1])
                            rooms[room].plans[0 if int(user) else 1].board[row][col] = -3 - int(plan[-1])
    return rooms[room].plans[int(user)].other


def player_wait(room: str, user: str):
    while 1:
        if isinstance(rooms[room].plans[int(user)], Plan) and rooms[room].plans[int(user)].attachable:
            return True
        time.sleep(0.5)


@app.route('/', methods=['GET'])
def index():
    res = make_response(render_template('index.html', msg='请输入房间号开始游戏'), 200)
    if not request.cookies.get('room'):
        room = request.args.get('room')
        if room:
            if room not in rooms:
                rooms[room] = Room(room)
                res.set_cookie('user', '0', max_age=21600)  # 默认登录6个小时
            elif len(rooms[room].plans) < 2:
                res.set_cookie('user', '1', max_age=21600)  # 默认登录6个小时
            else:
                return make_response(render_template('index.html', msg='该房间人员已满！'), 400)
            rooms[room].add(Plan())
            res.set_cookie('room', room, max_age=21600)  # 默认登录6个小时
    return res


@app.route('/wait_two_people', methods=['GET'])  # 尝试异步
def wait_two_people():
    if not request.cookies.get('room'):
        return make_response(render_template('index.html', msg='请输入房间号开始游戏'), 200)
    elif wait(request.cookies.get('room')):
        res = make_response(jsonify({'code': 0, 'msg': '对方已就绪！'}), 200)
        res.set_cookie('start', 'true', max_age=21600)
        return res


@app.route('/wait_plan', methods=['GET'])  # 尝试异步
def wait_plan():
    if not request.cookies.get('room'):
        return make_response(render_template('index.html', msg='请输入房间号开始游戏'), 200)
    elif plan_wait(request.cookies.get('room')):
        first = rooms[request.cookies.get('room')].plans[int(request.cookies.get('user'))].first
        if first:
            res = make_response(jsonify({'code': 0, 'msg': '双方飞机已放置完毕！游戏开始！你是先手！', 'first': first}), 200)
        else:
            res = make_response(jsonify({'code': 0, 'msg': '双方飞机已放置完毕！游戏开始！你是后手！', 'first': first}), 200)
        res.set_cookie('first', str(first).lower(), max_age=21600)
        return res


@app.route('/draw_player', methods=['GET'])  # 尝试异步
def draw_player():
    if not request.cookies.get('room'):
        return make_response(render_template('index.html', msg='请输入房间号开始游戏'), 200)
    else:
        return make_response(jsonify({'code': 0, 'board': player_draw(request.cookies.get('room'), request.cookies.get('user'), request.args.get('x'), request.args.get('y'))}), 200)


@app.route('/wait_player', methods=['GET'])  # 尝试异步
def wait_player():
    if not request.cookies.get('room'):
        return make_response(render_template('index.html', msg='请输入房间号开始游戏'), 200)
    else:
        if player_wait(request.cookies.get('room'), request.cookies.get('user')):
            return make_response(jsonify({'code': 0, 'msg': '轮到你攻击了~', 'board': rooms[request.cookies.get('room')].plans[int(request.cookies.get('user'))].board}), 200)


@app.route('/plans', methods=['GET'])
def plans():
    if not request.cookies.get('room'):
        res = make_response(render_template('index.html', msg='请输入房间号开始游戏'), 200)
    else:
        x, y, board, plan = request.args.get('x'), request.args.get('y'), request.args.get('board'), request.args.get('plan')
        if x and y and board and plan:
            rooms[request.cookies.get('room')].plans[int(request.cookies.get('user'))].set_site((int(x), int(y)), plan)
            board = eval(board)
            board[int(y) - 1][int(x) - 1] = 1 + int(plan[-1])
            rooms[request.cookies.get('room')].plans[int(request.cookies.get('user'))].set_board(board)
            res = make_response(jsonify({'code': 0, 'msg': '飞机放置成功！'}), 200)
        else:
            res = make_response('参数缺失！', 400)
    return res


@app.route('/get_plans', methods=['GET'])
def get_plans():
    if not request.cookies.get('room'):
        res = make_response(render_template('index.html', msg='请输入房间号开始游戏'), 200)
    else:
        res = make_response(jsonify(rooms[request.cookies.get('room')].plans[int(request.cookies.get('user'))].board), 200)
    return res


@app.route('/check', methods=['GET'])
def check():
    if not request.cookies.get('room'):
        res = make_response(render_template('index.html', msg='请输入房间号开始游戏'), 200)
    else:
        if rooms[request.cookies.get('room')].plans[int(request.cookies.get('user'))].kills.count(1) == 3:
            res = make_response('你输了！', 200)
            res.set_cookie('start', 'stop', max_age=21600)
        elif rooms[request.cookies.get('room')].plans[0 if int(request.cookies.get('user')) else 1].kills.count(1) == 3:
            res = make_response('你赢了！', 200)
            res.set_cookie('start', 'stop', max_age=21600)
        else:
            res = make_response('', 200)
    return res


@app.route('/logout', methods=['GET'])
def logout():
    rooms[request.cookies.get('room')].plans.pop()
    if not rooms[request.cookies.get('room')].plans:
        del rooms[request.cookies.get('room')]
    res = make_response(jsonify({'code': 0, 'msg': '退出房间成功！'}))
    res.delete_cookie('room')
    res.delete_cookie('user')
    res.delete_cookie('start')
    res.delete_cookie('first')
    return res


if __name__ == '__main__':
    # 第二代：js 元素双击旋转
    app.run(host='0.0.0.0', port=8866, threaded=True, processes=1)
