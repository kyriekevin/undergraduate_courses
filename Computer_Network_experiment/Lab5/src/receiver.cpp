#define _CRT_SECURE_NO_WARNINGS
#define _WINSOCK_DEPRECATED_NO_WARNINGS

#include "receiver.h"

// 构造函数，设置服务端信息
Server::Server() : listener{ 0 } {
	serverAddr.sin_family = PF_INET;
	serverAddr.sin_port = SERVER_PORT;
	serverAddr.sin_addr.s_addr = inet_addr(SERVER_IP);
}

// 初始化函数，创建监听套接字，绑定端口并进行监听
void Server::init() {
	int iRet;
	WORD ver = MAKEWORD(2, 2); // 使用版本2.2
	WSADATA data; // 用于初始化套接字环境
	iRet = WSAStartup(ver, &data);

	// 初始化WinSock环境
	if (iRet == SOCKET_ERROR) {
		cerr << "WSAStartup fail " << iRet << endl;
		WSACleanup();
	}
	else cout << "WSAStartup success" << endl;

	SOCKET sock = socket(AF_INET, SOCK_STREAM, 0); // 采用ipv4,TCP传输
	listener = sock;

	if (sock == INVALID_SOCKET) {
		cerr << "SOCKET fail " << WSAGetLastError() << endl;
		exit(-1);
	}
	else cout << "SOCKET success" << endl;

	unsigned long ul = 1;
	iRet = ioctlsocket(sock, FIONBIO, (unsigned long*)&ul);
	if (iRet == -1) {
		cerr << "ioctlsocket fail" << endl;
		exit(-1);
	}
	else cout << "ioctlsocket success" << endl;

	// 绑定网络端口
	iRet = bind(sock, (sockaddr*)&serverAddr, sizeof sockaddr_in);
	if (iRet == SOCKET_ERROR) {
		cerr << "bind fail" << endl;
		exit(-1);
	}
	else cout << "bind success" << endl;

	// listen监听
	iRet = listen(sock, 6);
	if (iRet == SOCKET_ERROR) {
		cerr << "listen fail" << endl;
		exit(-1);
	}
	else cout << "listen success" << endl;

	socNum.emplace_back(listener);
	return;
}

void Server::process() {
	int cnt = 0;
	fd_set fds;
	FD_ZERO(&fds);

	// 初始化，与服务端建立连接
	init();

	cout << "Waiting for client information......" << endl;
	while (true) {
		cnt = socNum.size();
		for (int i = 0; i < cnt; ++i)
			FD_SET(socNum[i], &fds);
		struct timeval timeout = { 1, 0 };

		switch (select(0, &fds, nullptr, nullptr, &timeout)) {
		case -1: {
			cerr << "select error: " << WSAGetLastError() << endl;
			Sleep(1000);
			break;
		}
		case 0: break;
		default: {
			// 将数组中的每一个套接字都和剩余的套接字进行比较
			for (int i = 0; i < cnt; ++i) {
				// 如果第一个有套接字可读的消息，就直接建立连接
				if (i == 0 && FD_ISSET(socNum[i], &fds)) {
					struct sockaddr_in clientAddress;
					socklen_t clientAddrLen = sizeof(struct sockaddr_in);
					// 返回一个用户的套接字
					SOCKET csock = accept(listener, (struct sockaddr*)&clientAddress, &clientAddrLen);
					if (csock == INVALID_SOCKET)
						cerr << "accept fail" << endl;
					else {
						cout << "accept success" << endl;
						int clientfd = csock;
						// 添加用户，服务器上显示消息，并通知用户连接成功
						socNum.emplace_back(clientfd);
						cout << "Client " << clientfd << " successfully connected to the server" << endl;
						char ID[1024];
						sprintf(ID, "Hello, your ID is %d", clientfd);

						// 服务器产生ID并发送给客户端让客户端知道自己的ID
						send(clientfd, ID, sizeof(ID) - 1, 0); // 扣掉最后一个结束符
					}
				}
				if (i != 0 && FD_ISSET(socNum[i], &fds)) {
					char buf[1024]{};
					memset(buf, '\0', sizeof buf);
					int size = recv(socNum[i], buf, sizeof(buf) - 1, 0);
					// 检测是否出现断线情况
					if (size == 0 || size == -1) {
						cerr << "Client " << socNum[i] << " is offline" << endl;
						// 关闭已掉线的套接字，并从列表和数组中删除
						closesocket(socNum[i]);
						FD_CLR(socNum[i], &fds);
						socNum.erase(socNum.begin() + i);
						cnt--;
					}
					else {
						cout << "Client " << socNum[i] << " said " << buf << endl;
						// 对用户发送过来的信息进行分割，提取出（序列号）用户名密码
						vector<string> info = split(buf);
						string str;
						if (info.size() == 2) {
							info[0] = "username: " + info[0];
							info[1] = "password: " + info[1];
							str = info[0] + " " + info[1];
						}
						else {
							info[0] = "serial number: " + info[0];
							info[1] = "username: " + info[1];
							info[2] = "password: " + info[2];
							str = info[0] + " " + info[1] + " " + info[2];
						}

						/*
							提取信息后进行校验，校验方法需要添加在这里
						*/

						// 将消息发送给发来消息的客户端
						char client[1024];
						sprintf(client, " Client %d", socNum[i]);
						strcat(client, str.c_str());
						send(socNum[i], client, sizeof(client) - 1, 0);
					}
				}
			}
			break;
		}
		}
	}
}

// 将输入的信息根据空格进行分割
vector<string> Server::split(char* str) {
	vector<string> item;
	const char* blank = " ";
	char* ch = strtok(str, blank);
	while (ch) {
		item.emplace_back(ch);
		ch = strtok(nullptr, blank);
	}

	return item;
}

int main() {
	Server server;
	server.process();

	return 0;
}