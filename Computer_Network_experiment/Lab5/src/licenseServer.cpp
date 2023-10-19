#include "server.h"
#pragma warning(disable : 4996)
using namespace std;

Server myServer;
queue<updateTuple> updateBuf; // 暂存待进行的更新
map<sockaddr_in, clientData> clientInfo; // 使用客户端地址查找客户端信息

bool operator<(const sockaddr_in& l, const sockaddr_in& r) {
	return l.sin_port < r.sin_port;
}

void readLicenseData() {
	// 读取证件中的信息
	return;
}

void connectClient(sockaddr_in clientAddr) {
	// 与对应的客户端交流
	// 设定一个计时器一段时间没收到check则关闭线程
	MSG msg;
	while (true) {
		if (PeekMessage(&msg, nullptr, 0, 0, PM_REMOVE)) {
			if (msg.message == CK_MSG) {
				// 重置计时器
			}
			if (msg.message == WM_QUIT) {
				return;
			}
		}
	}
}

bool checkInfo(string name, string pwd, string serialNum) {
	// 确认登录信息

	return true;
}

void updateLicense(updateTuple tuple) {
	// 对证件文件内容进行更新
	string status;
	if (tuple.status)
		status = "login";
	else status = "logout";
	cout << "user " << inet_ntoa(tuple.clientAddr.sin_addr) << "\t" << status << endl;
}

void handleMessage(messageData data) {
	// 处理来自客户端的信息
	cout << inet_ntoa(data.addr.sin_addr) << "\t" << data.msg << endl;
	stringstream ss;
	ss.str(data.msg);
	string input;
	cin >> input;

	// 三类消息指令,login登录,check定时汇报,quit退出
	if (input == "login") {
		string username, password, serialNum;
		cin >> username >> password >> serialNum;

		if (checkInfo(username, password, serialNum)) {
			// 确认信息无误向客户端发送允许登录指令
			// 创建新的线程管理与客户端的连接，并储存对应客户端的信息,向更新队列添加更新指令
			myServer.sendToClient(&(data.addr), "permit");
			thread* thr = new thread(connectClient, data.addr);
			clientInfo[data.addr] = clientData(data.addr, username, password, serialNum, thr);
			updateBuf.push(updateTuple(data.addr, true));
		}
		else myServer.sendToClient(&(data.addr), "Error message, login failed");
	}
	else if (input == "check") {
		// 根据地址找到对应的线程，重置线程时间
		thread* tr = clientInfo.at(data.addr).corrThread;
		DWORD gtid = GetThreadId(tr->native_handle());
		while (!PostThreadMessage(gtid, CK_MSG, 0, 0));
	}
	else if (input == "quit") {
		// 关闭对应线程，向更新队列添加更新指令
		thread* tr = clientInfo.at(data.addr).corrThread;
		DWORD gtid = GetThreadId(tr->native_handle());
		while (!PostThreadMessage(gtid, WM_QUIT, 0, 0));
		clientInfo.erase(data.addr);
		updateBuf.push(updateTuple(data.addr, false));
	}
	else myServer.sendToClient(&(data.addr), "Please enter the correct instructions");
}

int main() {
	readLicenseData();
	thread recvThread(&Server::receieveFromClient, &myServer);

	while (true) {
		if (!myServer.msgBuf.empty()) {
			// 如果消息队列不为空，就提取出一条消息进行处理
			handleMessage(myServer.msgBuf.front());
			myServer.msgBuf.pop();
		}
		if (!updateBuf.empty()) {
			// 如果更新队列不为空，就进行一次更新
			updateLicense(updateBuf.front());
			updateBuf.pop();
		}
	}

	recvThread.join();

	return 0;
}