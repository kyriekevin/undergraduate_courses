#include "client.h"
#pragma warning(disable : 4996)
using namespace std;

Client::Client() {
	init();
}

void Client::init() {
	int iRet;
	int port = 8307;
	WSADATA data;
	WORD ver = MAKEWORD(2, 1);
	string serverIP = "192.168.1.104";

	iRet = WSAStartup(ver, &data);
	if (iRet) {
		cerr << "WSAStartup fail" << endl;
		WSACleanup();
		exit(-1);
	}
	else cout << "WSAStartup success" << endl;

	serverAddr.sin_family = AF_INET; // UDP地址族
	serverAddr.sin_port = htons(port); // server监听端口
	serverAddr.sin_addr.S_un.S_addr = inet_addr(serverIP.c_str()); // server地址
	socket1 = socket(AF_INET, SOCK_DGRAM, 0); // 数据报格式用于无连接的UDP传输
}

void Client::sendToServer(string msg) {
	sendto(socket1, msg.c_str(), msg.size(), 0, (struct sockaddr*)&serverAddr, sizeof serverAddr);
}

string Client::receieveFromServer() {
	while (true) {
		char buf[128]{};
		memset(buf, '\0', sizeof buf);
		int msgLen = sizeof serverAddr;
		if (recvfrom(socket1, buf, sizeof buf, 0, (struct sockaddr*)&serverAddr, &msgLen) != SOCKET_ERROR)
			return string(buf);
	}
}