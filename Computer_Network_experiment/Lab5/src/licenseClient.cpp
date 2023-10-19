#include "client.h"
using namespace std;

Client myClient;

bool login(string username, string password, string serialNum) {
	// 向服务器发送信息登录
	myClient.sendToServer("login" + username + " " + password + " " + serialNum);
	string reply = myClient.receieveFromServer();
	if (reply == "permit") return true;
	else return false;
}

void check() {
	// 每经过一段时间对服务器发一个check
}

int main() {
	string username, password, serialNum;
	cout << "Please enter in the following format : [User Name] [Password] [Serial Number]" << endl;
	cin >> username >> password >> serialNum;
	while (!login(username, password, serialNum)) {
		cerr << "Logon failure" << endl;
		cout << "Please enter in the following format : [User Name] [Password] [Serial Number]" << endl;
		cin >> username >> password >> serialNum;
	}

	cout << "Log in successfully" << endl;
	thread check_thread(check);
	while (true) {
		cout << "Type quit to exit" << endl;
		string input;
		cin >> input;
		if (input == "quit") {
			myClient.sendToServer(input);
			break;
		}
	}

	return 0;
}