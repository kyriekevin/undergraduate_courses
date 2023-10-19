#ifndef CLIENT_H
#define CLIENT_H

#include <iostream>
#include <WinSock2.h>
#include <vector>
#include <string>
#include <map>
#include <queue>
#include <WS2tcpip.h>
#include <ctime>
#include <Windows.h>
#include <thread>
#pragma comment(lib, "WS2_32.lib")
using namespace std;

class Client {
	SOCKET socket1;
	sockaddr_in serverAddr;
	void init();
public:
	Client();
	void sendToServer(string msg);
	string receieveFromServer();
};

#endif // !CLIENT_H
