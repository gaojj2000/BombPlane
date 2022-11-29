var board = new Array(12).fill(new Array(12).fill(0));
var plan = [0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0];
var plan_ = [
	[0, 0, 1, 0, 0],
	[1, 1, 1, 1, 1],
	[0, 0, 1, 0, 0],
	[0, 1, 1, 1, 0],
];
var times = null;
var game = false;

function drag(event) {
	event.dataTransfer.setData('text', event.target.id);
}

function drop(event) {
	judge({
		'text': event.dataTransfer.getData('text'),
		'site': event.path[0]
	});
}

function allowDrop(event) {
	event.preventDefault();
}

function ajax(url, success_function) {
	var xhr = new XMLHttpRequest();
	xhr.open('GET', url, true); // xhr.open(method, url, async, username, password);
	// xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
	xhr.send(null);
	// xhr.abort();  // 调用这个方法后，XHR对象会停止触发事件，而且也不再允许访问任何与响应有关的对象属性。在终止请求之后，还应该对XHR对象进行解引用操作。由于内存原因，不建议重用XHR对象。
	var promise = new Promise(function(resolve, reject) {
		xhr.onload = function() {
			try {
				resolve(JSON.parse(xhr.response));
			} catch (e) {
				resolve(xhr.response);
			}
		};
		xhr.onerror = () => reject(xhr.statusText);
	});
	return promise.then((success) => {
		// console.log(success);
		success_function(success);
	}).catch((failed) => {
		console.log(failed);
	});
};

function show(msg, time) {
	function clear() {
		times = null;
		note.style.display = 'none';
	}
	note.innerText = msg;
	note.style.display = 'block';
	if (times) {
		clearTimeout(times);
	}
	times = setTimeout(clear, time);
}

function judge(obj) {
	var site = parseInt(obj.site.id.slice(2));
	var x = site % 12 + 1;
	var y = Math.ceil((site + 1) / 12);
	if (x < 3 || x > 10 || y < 2 || y > 10) { // 判断飞机放下是否超出边界
		show('飞机不能超出边界哦！', 2000);
		return false;
	}
	for (var n2 = y - 2; n2 <= y + 1; n2++) {
		for (var n1 = x - 3; n1 <= x + 1; n1++) {
			if (board[n2][n1] && plan_[n2 - y + 2][n1 - x + 3]) {
				show('此处已有其他飞机了！', 2000);
				return false;
			}
		}
	}

	function draw(success) {
		show('飞机' + text + '放置成功！', 2000);
	}

	draw_plane(site = site, x = x, y = y, text = obj.text);
	ajax('/plans?x=' + x + '&y=' + y + '&board=' + JSON.stringify(board) + '&plan=' + obj.text, draw);
}

function draw_plane(site, x, y, text) {
	for (var n2 = y - 2; n2 <= y + 1; n2++) {
		var temp = new Array(12).fill(0);
		for (var n1 = x - 3; n1 <= x + 1; n1++) {
			var grid = document.getElementById('l_' + (n2 * 12 + n1));
			temp[n1] = plan_[n2 - y + 2][n1 - x + 3];
			if (plan_[n2 - y + 2][n1 - x + 3]) {
				if (site == (n2 * 12 + n1)) {
					grid.style.width = '48px';
					grid.style.height = '48px';
					grid.innerText = text;
					grid.style.border = '1px red dashed';
					grid.style.textAlign = 'center';
					grid.style.lineHeight = '50px';
					temp[n1] = plan_[n2 - y + 2][n1 - x + 3] + parseInt(text.slice(4, 5));
				}
				grid.style.backgroundColor = '#25a0e4';
			}
		}
		for (var i = 0; i < 12; i++) {
			if (board[n2][i]) {  // 将整行中原本是有飞机部分的重新赋值上！
				temp[i] = board[n2][i];
			}
		}
		board[n2] = temp;
	}
	document.getElementById(text).remove();
}

function draw_board(board_, area) {
	board = board_;
	area = area || 'l_';  // 使用 r_ 表示右边
	var index = 0;
	Array.prototype.forEach.call(board, function(row) {
		Array.prototype.forEach.call(row, function(col) {
			var grid = document.getElementById(area + index);
			if (col >= 2 || col <= -4) {
				grid.style.width = '48px';
				grid.style.height = '48px';
				grid.style.border = '1px red dashed';
				grid.style.textAlign = 'center';
				grid.style.lineHeight = '48px';
				if (col >= 2) {
					grid.innerText = "plan" + (col - 1);
					if (document.getElementById("plan" + (col - 1))) {
						document.getElementById("plan" + (col - 1)).remove();
					}
				}
				else {
					grid.innerText = "plan" + (-3 - col);
					if (document.getElementById("plan" + (-3 - col))) {
						document.getElementById("plan" + (-3 - col)).remove();
					}
				}
			}
			if (col < 0) {
				grid.onclick = null;
			}
			grid.style.backgroundColor = !col ? 'rgba(37, 160, 228, 0.4)' : col > 0 ? '#25a0e4' : col == -1 ? 'white' : col == -2 ? 'red' : 'gray';
			index += 1
		});
	});
}

function left_change(obj) {
	draw_board(eval(obj).board, 'r_');
	ajax('/check', check_win);
	ajax('/wait_player', draw_left);
}

function draw_left(success) {
	draw_board(success.board);
	game = true;
	show(success.msg, 1000);
	ajax('/check', check_win);
	
}

function right_change(obj) {
	if (game) {
		var site = parseInt(obj.slice(2));
		var x = site % 12 + 1;
		var y = Math.ceil((site + 1) / 12);
		game = false;
		show('等待对方攻击~', 1000);
		ajax('/draw_player?x=' + x + '&y=' + y, left_change);
	}
	ajax('/check', check_win);
}

function check_win(success) {
	if (success) {
		game = false;
		var index = 0;
		out.style.display = 'block';
		Array.prototype.forEach.call(board, function(row) {
			Array.prototype.forEach.call(row, function(col) {
				var grid = document.getElementById('r_' + index);
				grid.onclick = null;
				index += 1
			});
		});
		show(success, 10000);
	}
}

function logout() {
	ajax('/logout', refreash);
}

function refreash(success) {
	window.location.href = "/";
}

window.onload = function() {
	var out = document.getElementById('out');
	var note = document.getElementById('note');
	var left = document.getElementById('left');
	var right = document.getElementById('right');
	var plan1 = document.getElementById('plan1');
	var plan2 = document.getElementById('plan2');
	var plan3 = document.getElementById('plan3');
	var plans = [plan1, plan2, plan3];

	function init_game() {
		document.getElementById('start').style.display = 'none';
		var items = document.getElementsByClassName('sky');
		Array.prototype.forEach.call(items, function(item) {
			item.style.display = 'block'
		});
		for (var i = 0; i < 12 * 12; i++) {
			grid = document.createElement('div');
			grid.style.width = '50px';
			grid.style.height = '50px';
			grid.style.float = 'left';
			grid.id = 'l_' + i;
			grid.style.borderRadius = '10px';
			grid.style.backgroundColor = 'rgba(37, 160, 228, 0.4)';
			// ondrop='drop(event)' ondragover='allowDrop(event)'
			// grid.ondrag = 'drop(event)';
			// grid.ondragover = 'allowDrop(event)';
			grid.onclick = null;
			left.appendChild(grid);
		};
		for (var i = 0; i < 12 * 12; i++) {
			grid = document.createElement('div');
			grid.style.width = '50px';
			grid.style.height = '50px';
			grid.style.float = 'left';
			grid.id = 'r_' + i;
			grid.style.borderRadius = '10px';
			grid.style.backgroundColor = 'rgba(37, 160, 228, 0.4)';
			grid.onclick = function(x) {
				return right_change(x.target.id);
			};
			right.appendChild(grid);
		};
		for (var p = 0; p < 3; p++) {
			for (var i = 0; i < plan.length; i++) {
				grid = document.createElement('div');
				grid.style.width = '50px';
				grid.style.height = '50px';
				grid.style.float = 'left';
				grid.style.border = '0';
				if (plan[i]) {
					if (i == 7) {
						grid.style.width = '48px';
						grid.style.height = '48px';
						grid.innerText = 'plan' + (p + 1);
						grid.style.border = '1px red dashed';
						grid.style.textAlign = 'center';
						grid.style.lineHeight = '48px';
					}
					grid.style.backgroundColor = '#25a0e4';
				}
				grid.id = 'p_' + p + 'l_' + i;
				plans[p].appendChild(grid);
				plans[p].style.display = 'block';
			}
		}
	}

	function play(success) {
		init_game();
		show('加载完成！开始放飞机吧~', 2000);
		ajax('/wait_plan', game_start);
	}
	
	function game_start(success) {
		show(success.msg, 2000);
		if (success.first) {
			game = true;
		}
		else {
			ajax('/wait_player', draw_left);
		}
	}

	function init(success) {
		draw_board(eval(success));
	}

	if (document.cookie) {
		if (document.cookie.indexOf('start=true') != -1) {
			init_game();
			ajax('/get_plans', init);
			ajax('/draw_player?x=-1&y=-1', left_change);
			ajax('/wait_player', draw_left);
		} else if (document.cookie.indexOf('start=stop') != -1) {
			ajax('/check', check_win);
		} else if (document.cookie.indexOf('user=') != -1) {
			var res = document.cookie.slice(document.cookie.indexOf('room='));
			var end = res.length;
			if (res.indexOf(';') != -1) {
				end = res.indexOf(';');
			}
			document.getElementById('room').innerHTML = '房间号为 ' + res.slice(5, end);
			res = document.cookie.slice(document.cookie.indexOf('user='));
			document.getElementById('res').innerHTML = '等待对方进入房间...';
			var p = document.createElement('p');
			var button = document.createElement('button');
			button.innerHTML = '退出登录';
			button.onclick = logout;
			p.appendChild(button);
			document.getElementById('start').appendChild(p);
			ajax('/wait_two_people', play);
		} else if (window.location.href.indexOf('?room=') != -1) {
			refreash();
		}
	}
};
