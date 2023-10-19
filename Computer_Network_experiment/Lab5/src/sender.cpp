#define _WINSOCK_DEPRECATED_NO_WARNINGS
#define _CRT_SECURE_NO_WARNINGS
#include "sender.h"
using namespace std;

string serialNumber; // 用户输入的序列号
bool status = false; // false表示服务器没有崩溃，true表示服务器崩溃

// 设置客户端信息
Client::Client() : user{ 0 }, writing{ 0 } {
	serverAddr.sin_family = PF_INET; // ipv4
	serverAddr.sin_port = SERVER_PORT; // host to net  unsigned short 服务器端口号
	serverAddr.sin_addr.s_addr = inet_addr(SERVER_IP); // 服务器地址
}

// 进行初始化，返回0表示初始化成功，返回-1表示初始化失败，需要尝试连接服务器
int Client::init() {
	int iRet;
	WORD ver = MAKEWORD(2, 2); // 使用版本2.2
	WSADATA data; // 用于初始化套接字环境
	iRet = WSAStartup(ver, &data);

	if (iRet == SOCKET_ERROR) {
		cerr << "WSAStartup() fail " << iRet << endl;
		WSACleanup();
	}
	else cout << "WSAStartup success" << endl;

	// 创建套接字
	SOCKET sock = socket(AF_INET, SOCK_STREAM, 0); // 采用ipv4,TCP传输
	user = sock;

	if (sock <= 0) {
		cerr << "connect fail " << WSAGetLastError() << endl;
		exit(-1);
	}

	// 阻塞式地等待服务器连接
	iRet = connect(sock, (sockaddr*)&serverAddr, sizeof sockaddr_in);
	if (iRet < 0) {
		cerr << "connect fail " << WSAGetLastError() << endl;
		return -1;
	}

	cout << "connect IP: " << SERVER_IP << " Port: " << SERVER_PORT << " success" << endl;
	return 0;
}

void Client::process() {
	char recvBuf[1024] = {};
	fd_set fdRead, fdWrite;
	FD_ZERO(&fdRead);
	FD_ZERO(&fdWrite);

	int flag = init();
	if (flag == -1) {
		Sleep(10000); // 10秒后尝试重新连接服务器
		return;
	}

	while (true) {
		FD_SET(user, &fdRead);
		if (writing == 0)
			FD_SET(user, &fdWrite);
		struct timeval timeout = { 1, 0 }; // 设置每隔1秒select一次
		switch (select(0, &fdRead, &fdWrite, nullptr, &timeout)) {
		case -1: {
			cerr << "error: " << WSAGetLastError() << endl;
			break;
		}
		case 0:
			break;
		default: {
			// 接收服务端发送回的信息
			if (FD_ISSET(user, &fdRead)) {
				int size = recv(user, recvBuf, sizeof(recvBuf) - 1, 0);
				if (size > 0) {
					cerr << "Server reply: " << recvBuf << endl;
					memset(recvBuf, '\0', sizeof recvBuf);
				}
				else {
					cout << "The server is closed and waiting for the server to start" << endl;
					Sleep(10000);
					cout << "Begin trying to reconnect to the server" << endl;
					status = true;
					return;
				}
			}
			if (FD_ISSET(user, &fdWrite)) {
				FD_ZERO(&fdWrite);
				writing = 1; // 表示写状态
				sendData();
			}
			break;
		}
		}
	}
}

// 将输入的信息根据空格进行分割
vector<string> Client::split(char* str) {
	vector<string> item;
	const char* blank = " ";
	char* ch = strtok(str, blank);
	while (ch) {
		item.emplace_back(ch);
		ch = strtok(nullptr, blank);
	}

	return item;
}

// 判断输入的字符串是否全部由数字组成，如果是返回true，否则返回false
bool Client::isNum(string str) {
	bool flag = true;
	for (auto ch : str) {
		if (ch < '0' || ch > '9') {
			flag = false;
			break;
		}
	}

	return flag;
}

void Client::getInfo(string& input, vector<string>& info) {
	getline(cin, input);
	info.clear();
	// 从用户输入的信息中截取出序列号，用户名和密码
	info = split((char*)input.c_str());

	return;
}

void Client::sendData() {
	string input;
	vector<string> info;
	getInfo(input, info);

	// 对输入的信息进行校验，没有错误则向服务端发送信息
	while (true) {
		if (info.size() < 2 || info.size() > 3) {
			cerr << "Please enter at least a username and password" << endl;
			cerr << "And please enter the serial number, username, password or username, password in the order separated by Spaces" << endl;
			getInfo(input, info);
			continue;
		}
		// 如果输入的为三项，则表明有输入序列号，则要对序列号进行检验
		else if (info.size() == 3) {
			serialNumber = info[0];
			if (serialNumber.size() != 10) {
				cerr << "The serial number should be 10 in length.Please re-enter all information: " << endl;
				getInfo(input, info);
				continue;
			}
			else if (!isNum(serialNumber)) {
				cerr << "The serial number was incorrectly entered.Please re-enter all information:" << endl;
				getInfo(input, info);
				continue;
			}
			else break;
		}
		else break; // 如果输入的为两项，表明没有序列号，则不需要进行检验
	}

	// 将客户端输入的序列号发送给服务端以求验证
	string str;
	if (info.size() == 3) str = info[0] + " " + info[1] + " " + info[2];
	else str = info[0] + " " + info[1];

	send(user, str.c_str(), sizeof str, 0);
	writing = 0;

	return;
}

int main() {
	Client user;
	while (true) user.process();

	return 0;
}