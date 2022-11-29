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
		console.log(success);
		success_function(success);
	}).catch((failed) => {
		console.log(failed);
	});
};

function refreash(success) {
	window.location.href = "/";
};

function drag(event) {
	event.dataTransfer.setData('text', event.target.id);
};

function drop(event) {
	ajax('/draw_plan?plan=' + event.dataTransfer.getData('text') + '&site=' + event.path[0].id.slice(2), refreash);
};

function allowDrop(event) {
	event.preventDefault();
};

function set_direction(plan) {
	ajax('/set_direction?plan=' + plan, refreash);
}

function attack(event) {
	ajax('/attack?site=' + event.id.slice(2), refreash);
};

function logout() {
	ajax('/logout', refreash);
};
