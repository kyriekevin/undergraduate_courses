#ifndef RECEIVER_H
#define RECEIVER_H

#include <iostream>
#include <WinSock2.h>
#include <vector>
#include <WS2tcpip.h>
#pragma comment(lib,"ws2_32.lib")
using namespace std;

#define SERVER_IP "192.168.1.104"  // 默认服务器端IP地址
#define SERVER_PORT 8307 // 服务器端口号

class Server {
private:
	int listener; // 监听套接字
	sockaddr_in serverAddr; // IPV4地址
	vector<int> socNum; // 存放创建的套接字

public:
	Server();
	void init();
	void process();
	vector<string> split(char* str);
};

#endif // !RECEIVER_H
