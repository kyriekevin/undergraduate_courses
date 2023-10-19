#include "server.h"
using namespace std;

Server::Server() {
	init();
}

void Server::init() {
	int iRet;
	int port = 8307;
	string serverIP = "192.168.1.104";
	WSADATA data;
	WORD ver = MAKEWORD(2, 1);
	iRet = WSAStartup(ver, &data);

	if (iRet) {
		cerr << "WSAStartup fail" << endl;
		WSACleanup();
		exit(-1);
	}
	else cout << "WSAStartup success" << endl;

	serverAddr.sin_family = AF_INET;
	serverAddr.sin_port = htons(port);
	serverAddr.sin_addr.S_un.S_addr = htonl(INADDR_ANY);
	socket1 = socket(AF_INET, SOCK_DGRAM, 0);
	bind(socket1, (struct sockaddr*)&serverAddr, sizeof serverAddr); // 将那个结构体绑定到当前的套接字绑定地址以及端口

	return;
}

void Server::sendToClient(sockaddr_in* clientAddr, string msg) {
	sendto(socket1, msg.c_str(), msg.size(), 0, (struct sockaddr*)&clientAddr, sizeof(*clientAddr));
}

void Server::receieveFromClient() {
	cout << "Start receiving messages" << endl;
	while (true) {
		char buf[128]{};
		memset(buf, '\0', sizeof buf);
		sockaddr_in clientAddr;
		int msgLen = sizeof(clientAddr);
		if (recvfrom(socket1, buf, sizeof buf, 0, (struct sockaddr*)&clientAddr, &msgLen) != SOCKET_ERROR)
			msgBuf.push(messageData(string(buf), clientAddr));
	}
}