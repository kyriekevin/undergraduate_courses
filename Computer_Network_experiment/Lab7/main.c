#define _GNU_SOURCE
#include <sys/types.h>
#include <stdio.h>
#include <stdarg.h> // 让函数能够接收可变参数
#include <time.h>
#include <errno.h>
#include <unistd.h> // 提供对POSIX操作系统API的访问功能
#include <signal.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
//#include <sys/socket.h>
#include <winsock2.h>
#pragma comment(lib,"ws2_32.lib")

#include <sys/fcntl.h>
#include <sys/stat.h>
#include <netdb.h>
#include <sys/select.h>
#include <arpa/inet.h>
#include <netinet/tcp.h>
#include <pthread.h>

#define BUFSIZE 65536
#define IPSIZE 4
#define ARRAY_SIZE(x) (sizeof(x) / sizeof(x[0]))
#define ARRAY_INIT    {0}

unsigned short int port = 1080;
int daemon_mode = 0;
int auth_type;
char* arg_username;
char* arg_password;
FILE* log_file;
pthread_mutex_t lock;

enum socks {
	RESERVED = 0x00,
	VERSION4 = 0x04,
	VERSION5 = 0x05
};

enum socks_auth_methods {
	NOAUTH = 0x00,
	USERPASS = 0x02,
	NOMETHOD = 0xff
};

enum socks_auth_userpass {
	AUTH_OK = 0x00,
	AUTH_VERSION = 0x01,
	AUTH_FAIL = 0xff
};

enum socks_command {
	CONNECT = 0x01
};

enum socks_command_type {
	IP = 0x01,
	DOMAIN = 0x03
};

enum socks_status {
	OK = 0x00,
	FAILED = 0x05
};

// 输出日志信息
void log_message(const char* message, ...)
{
	if (daemon_mode) {
		return;
	}

	char vbuffer[255];
	// 尝试在申请空间中进行打印操作
	va_list args; // 定义一个va_list型的变量,这个变量是指向参数的指针
	va_start(args, message); // 用va_start宏初始化变量,这个宏的第二个参数是第一个可变参数的前一个参数,是一个固定的参数
	vsnprintf(vbuffer, ARRAY_SIZE(vbuffer), message, args); // linux环境用法
	// 执行成功，返回最终生成字符串的长度，若生成字符串的长度大于size，则将字符串的前size个字符复制到str，同时将原串的长度返回
	// 执行失败，返回负值，并置errno
	va_end(args); // 用va_end宏结束可变参数的获取

	time_t now;
	time(&now);
	char* date = ctime(&now);
	date[strlen(date) - 1] = '\0';

	pthread_t self = pthread_self();

	if (errno != 0) {
		pthread_mutex_lock(&lock);
		fprintf(log_file, "[%s][%lu] Critical: %s - %s\n", date, self,
			vbuffer, strerror(errno));
		errno = 0;
		pthread_mutex_unlock(&lock);
	}
	else {
		fprintf(log_file, "[%s][%lu] Info: %s\n", date, self, vbuffer);
	}
	fflush(log_file);
}

int readn(int fd, void* buf, int n)
{
	int nread, left = n;
	while (left > 0) {
		if ((nread = read(fd, buf, left)) == -1) {
			// 当有错误发生时则返回-1, 错误代码存入errno中, 而文件读写位置则无法预期
			if (errno == EINTR || errno == EAGAIN) {
				// EINTR 此调用被信号所中断
				// EAGAIN 当使用不可阻断I/O 时(O_NONBLOCK), 若无数据可读取则返回此值
				continue;
			}
		}
		else {
			if (nread == 0) {
				return 0;
			}
			else {
				left -= nread;
				buf += nread;
			}
		}
	}
	return n;
}

int writen(int fd, void* buf, int n)
{
	int nwrite, left = n;
	while (left > 0) {
		// 如果顺利write()会返回实际写入的字节数. 当有错误发生时则返回-1, 错误代码存入errno中
		if ((nwrite = write(fd, buf, left)) == -1) {
			if (errno == EINTR || errno == EAGAIN) {
				continue;
			}
		}
		else {
			if (nwrite == n) {
				return 0;
			}
			else {
				left -= nwrite;
				buf += nwrite;
			}
		}
	}
	return n;
}

void app_thread_exit(int ret, int fd)
{
	close(fd);
	pthread_exit((void*)&ret);
}

int app_connect(int type, void* buf, unsigned short int portnum)
{
	int fd;
	struct sockaddr_in remote;
	/*
	* struct sockaddr_in {
	*	sa_family_t		sin_family; // 地址族(Address Family)
	*	uint16_t		sin_port;	// 16位TCP/UDP端口号
	*	struct in_addr	sin_addr;	// 32位IP地址
	*	char			sin_zero[8];// 不使用,一般用0填充
	* }
	*/
	char address[16];

	memset(address, 0, ARRAY_SIZE(address));

	if (type == IP) {
		char* ip = (char*)buf;
		snprintf(address, ARRAY_SIZE(address), "%hhu.%hhu.%hhu.%hhu",
			ip[0], ip[1], ip[2], ip[3]);
		memset(&remote, 0, sizeof(remote));
		remote.sin_family = AF_INET; // AF_INET TCP/IP --IPv4
		remote.sin_addr.s_addr = inet_addr(address); // 将一个IP字符串转化成一个网络字节序的整数值
		remote.sin_port = htons(portnum); // htons 针对两个字节，16位

		fd = socket(AF_INET, SOCK_STREAM, 0); // 创建套接字 SOCK_STREAM 流格式套接字/面向连接的套接字
		if (connect(fd, (struct sockaddr*)&remote, sizeof(remote)) < 0) { // 建立连接
			/*
			* int connect(int sock, struct sockaddr *addr, socklen_t addrlen);
			* sock 为socket文件描述符, addr为sockaddr结构体变量指针，addrlen为addr变量大小，由sizeof计算得出
			* sin_family和socket()的第一个参数的含义相同，取值时要保持一致
			* sin_zero[8]是多余的8个字节，没有用，一般使用memset填充为0。前面全部字节填充为0，前三个成员赋值，sin_zero就是为0
			*
			* struct sockaddr {
			*	sa_family_t		sin_family; // 地址族(Address Family)
			*	char			sa_data[14];// IP地址和端口号
			* }
			* sockaddr和sockaddr_in长度相同，都是16字节，只是将IP地址和端口号合并在一起，用一个成员表示
			* 要给sa_data赋值就必须同时指明IP地址和端口号，但没有相关函数将这个字符转换成所需要的形式
			* 所以使用sockaddr_in来代替，两个结构体长度相同，强制转换类型时不会丢失字节，也没有多余字节
			*/
			log_message("connect() in app_connect");
			close(fd);
			return -1;
		}

		return fd;
	}
	else if (type == DOMAIN) {
		char portaddr[6];
		struct addrinfo* res;
		/*
		* struct addrinfo {
		*	int ai_flags;				// Input flags
		*	int ai_family;				// Protocol family for socket
		*	int ai_socktype;			// Socket type
		*	int ai_protocol				// Protocol for socket
		*	socklen_t ai_addrlen		// Length of socket address
		*	struct sockaddr *ai_addr	// Socket address for socket
		*	char *ai_cannoname			// Cannonical name for service location
		*	struct addrinfo *ai_next	// Pointer to next in list
		* };
		*/
		snprintf(portaddr, ARRAY_SIZE(portaddr), "%d", portnum);
		log_message("getaddrinfo: %s %s", (char*)buf, portaddr);
		int ret = getaddrinfo((char*)buf, portaddr, NULL, &res);
		/*
		* int getaddrinfo(const char* nodename, const char* servname, const struct addrinfo* ints, struct addrinfo** res);
		* nodename:节点名可以是主机名，也可以是数字地址 IPv4点分十进制
		* servname:包含十进制数的端口号或服务器名
		* hints:一个空指针或指向一个addrinfo结构的指针
		* res:存放返回addrinfo结构链表的指针，指向由一个或多个addrinfo结构体组成的链表，包含主机的响应信息
		* 返回值:成功返回0，失败返回非零的sockets error code
		*/
		if (ret == EAI_NODATA) {
			return -1;
		}
		else if (ret == 0) {
			struct addrinfo* r;
			for (r = res; r != NULL; r = r->ai_next) {
				fd = socket(r->ai_family, r->ai_socktype,
					r->ai_protocol);
				if (fd == -1) {
					continue;
				}
				ret = connect(fd, r->ai_addr, r->ai_addrlen);
				if (ret == 0) {
					freeaddrinfo(res);
					return fd;
				}
				else {
					close(fd);
				}
			}
		}
		freeaddrinfo(res);
		return -1;
	}

	return -1;
}

// 初始化
int socks_invitation(int fd, int* version)
{
	char init[2];
	int nread = readn(fd, (void*)init, ARRAY_SIZE(init));
	if (nread == 2 && init[0] != VERSION5 && init[0] != VERSION4) {
		log_message("They send us %hhX %hhX", init[0], init[1]);
		log_message("Incompatible version!");
		app_thread_exit(0, fd);
	}
	log_message("Initial %hhX %hhX", init[0], init[1]);
	*version = init[0];
	return init[1];
}

// 获取用户名
char* socks5_auth_get_user(int fd)
{
	unsigned char size;
	readn(fd, (void*)&size, sizeof(size));

	char* user = (char*)malloc(sizeof(char) * size + 1);
	readn(fd, (void*)user, (int)size);
	user[size] = 0;

	return user;
}

// 获取密码
char* socks5_auth_get_pass(int fd)
{
	unsigned char size;
	readn(fd, (void*)&size, sizeof(size));

	char* pass = (char*)malloc(sizeof(char) * size + 1);
	readn(fd, (void*)pass, (int)size);
	pass[size] = 0;

	return pass;
}

int socks5_auth_userpass(int fd)
{
	char answer[2] = { VERSION5, USERPASS };
	writen(fd, (void*)answer, ARRAY_SIZE(answer));
	char resp;
	readn(fd, (void*)&resp, sizeof(resp));
	log_message("auth %hhX", resp);
	char* username = socks5_auth_get_user(fd);
	char* password = socks5_auth_get_pass(fd);
	log_message("l: %s p: %s", username, password);
	// 用户信息正确
	if (strcmp(arg_username, username) == 0
		&& strcmp(arg_password, password) == 0) {
		char answer[2] = { AUTH_VERSION, AUTH_OK };
		writen(fd, (void*)answer, ARRAY_SIZE(answer));
		free(username);
		free(password);
		return 0;
	}
	// 用户信息错误
	else {
		char answer[2] = { AUTH_VERSION, AUTH_FAIL };
		writen(fd, (void*)answer, ARRAY_SIZE(answer));
		free(username);
		free(password);
		return 1;
	}
}

int socks5_auth_noauth(int fd)
{
	char answer[2] = { VERSION5, NOAUTH };
	writen(fd, (void*)answer, ARRAY_SIZE(answer));
	return 0;
}

void socks5_auth_notsupported(int fd)
{
	char answer[2] = { VERSION5, NOMETHOD };
	writen(fd, (void*)answer, ARRAY_SIZE(answer));
}

void socks5_auth(int fd, int methods_count)
{
	int supported = 0;
	int num = methods_count;
	for (int i = 0; i < num; i++) {
		char type;
		readn(fd, (void*)&type, 1);
		log_message("Method AUTH %hhX", type);
		if (type == auth_type) {
			supported = 1;
		}
	}
	if (supported == 0) {
		socks5_auth_notsupported(fd);
		app_thread_exit(1, fd);
	}
	int ret = 0;
	switch (auth_type) {
	case NOAUTH:
		ret = socks5_auth_noauth(fd);
		break;
	case USERPASS:
		ret = socks5_auth_userpass(fd);
		break;
	}
	if (ret == 0) {
		return;
	}
	else {
		app_thread_exit(1, fd);
	}
}

int socks5_command(int fd)
{
	char command[4];
	readn(fd, (void*)command, ARRAY_SIZE(command));
	log_message("Command %hhX %hhX %hhX %hhX", command[0], command[1],
		command[2], command[3]);
	return command[3];
}

unsigned short int socks_read_port(int fd)
{
	unsigned short int p;
	readn(fd, (void*)&p, sizeof(p));
	log_message("Port %hu", ntohs(p));
	return p;
}

char* socks_ip_read(int fd)
{
	char* ip = (char*)malloc(sizeof(char) * IPSIZE);
	readn(fd, (void*)ip, IPSIZE);
	log_message("IP %hhu.%hhu.%hhu.%hhu", ip[0], ip[1], ip[2], ip[3]);
	return ip;
}

void socks5_ip_send_response(int fd, char* ip, unsigned short int port)
{
	char response[4] = { VERSION5, OK, RESERVED, IP };
	writen(fd, (void*)response, ARRAY_SIZE(response));
	writen(fd, (void*)ip, IPSIZE);
	writen(fd, (void*)&port, sizeof(port));
}

char* socks5_domain_read(int fd, unsigned char* size)
{
	unsigned char s;
	readn(fd, (void*)&s, sizeof(s));
	char* address = (char*)malloc((sizeof(char) * s) + 1);
	readn(fd, (void*)address, (int)s);
	address[s] = 0;
	log_message("Address %s", address);
	*size = s;
	return address;
}

void socks5_domain_send_response(int fd, char* domain, unsigned char size,
	unsigned short int port)
{
	char response[4] = { VERSION5, OK, RESERVED, DOMAIN };
	writen(fd, (void*)response, ARRAY_SIZE(response));
	writen(fd, (void*)&size, sizeof(size));
	writen(fd, (void*)domain, size * sizeof(char));
	writen(fd, (void*)&port, sizeof(port));
}

int socks4_is_4a(char* ip)
{
	return (ip[0] == 0 && ip[1] == 0 && ip[2] == 0 && ip[3] != 0);
}

int socks4_read_nstring(int fd, char* buf, int size)
{
	char sym = 0;
	int nread = 0;
	int i = 0;

	while (i < size) {
		nread = recv(fd, &sym, sizeof(char), 0);

		if (nread <= 0) {
			break;
		}
		else {
			buf[i] = sym;
			i++;
		}

		if (sym == 0) {
			break;
		}
	}

	return i;
}

void socks4_send_response(int fd, int status)
{
	char resp[8] = { 0x00, (char)status, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 };
	writen(fd, (void*)resp, ARRAY_SIZE(resp));
}

void app_socket_pipe(int fd0, int fd1)
{
	int maxfd, ret;
	fd_set rd_set; // 一组文件描述字的集合，它用一位来表示一个fd
	size_t nread;
	char buffer_r[BUFSIZE];

	log_message("Connecting two sockets");

	maxfd = (fd0 > fd1) ? fd0 : fd1;
	while (1) {
		FD_ZERO(&rd_set); // 将指定的文件描述符集清空，在对文件描述符集合进行设置前，必须清空
		// 不清空，由于在系统分配内存空间后，通常不作清空处理，结果是不可知的
		FD_SET(fd0, &rd_set); // 用于在文件描述符集合中增加一个新的文件描描述符
		FD_SET(fd1, &rd_set);
		ret = select(maxfd + 1, &rd_set, NULL, NULL, NULL);
		/*
		* int select(int maxfd, fd_set *rdset, fd_set *wrset, fd_set *exset, struct timeval *timeout);
		* maxfd是需要监视的最大的文件描述符值+1
		* rdset是需要检测的可读文件描述符的集合
		* wrset是可写文件描述符的集合
		* exset是异常文件描述符的集合
		* struct timeval结构用于描述一段时间长度，如果在这个时间内，需要监视的描述符没有事件发生则函数返回，返回值为0
		*/

		if (ret < 0 && errno == EINTR) {
			continue;
		}

		if (FD_ISSET(fd0, &rd_set)) { // FD_ISSET 用于测试指定的文件描述符是否在该集合中
			nread = recv(fd0, buffer_r, BUFSIZE, 0);
			if (nread <= 0)
				break;
			send(fd1, (const void*)buffer_r, nread, 0);
		}

		if (FD_ISSET(fd1, &rd_set)) {
			nread = recv(fd1, buffer_r, BUFSIZE, 0);
			if (nread <= 0)
				break;
			send(fd0, (const void*)buffer_r, nread, 0);
		}
	}
}

// app线程
void* app_thread_process(void* fd)
{
	int net_fd = *(int*)fd;
	int version = 0;
	int inet_fd = -1;
	// 判断版本
	char methods = socks_invitation(net_fd, &version);

	switch (version) {
	case VERSION5: {
		socks5_auth(net_fd, methods);
		// 获取命令，判断是对IP处理还是对域处理
		int command = socks5_command(net_fd);

		if (command == IP) {
			// 获取ip和端口
			char* ip = socks_ip_read(net_fd);
			unsigned short int p = socks_read_port(net_fd);

			inet_fd = app_connect(IP, (void*)ip, ntohs(p));
			if (inet_fd == -1) {
				app_thread_exit(1, net_fd);
			}
			socks5_ip_send_response(net_fd, ip, p);
			free(ip);
			break;
		}
		else if (command == DOMAIN) {
			unsigned char size;
			// 获取域和端口
			char* address = socks5_domain_read(net_fd, &size);
			unsigned short int p = socks_read_port(net_fd);

			inet_fd = app_connect(DOMAIN, (void*)address, ntohs(p));
			if (inet_fd == -1) {
				app_thread_exit(1, net_fd);
			}
			socks5_domain_send_response(net_fd, address, size, p);
			free(address);
			break;
		}
		else {
			app_thread_exit(1, net_fd);
		}
	}
	case VERSION4: {
		if (methods == 1) {
			char ident[255];
			unsigned short int p = socks_read_port(net_fd);
			char* ip = socks_ip_read(net_fd);
			socks4_read_nstring(net_fd, ident, sizeof(ident));

			if (socks4_is_4a(ip)) {
				char domain[255];
				socks4_read_nstring(net_fd, domain, sizeof(domain));
				log_message("Socks4A: ident:%s; domain:%s;", ident, domain);
				inet_fd = app_connect(DOMAIN, (void*)domain, ntohs(p));
			}
			else {
				log_message("Socks4: connect by ip & port");
				inet_fd = app_connect(IP, (void*)ip, ntohs(p));
			}

			if (inet_fd != -1) {
				socks4_send_response(net_fd, 0x5a);
			}
			else {
				socks4_send_response(net_fd, 0x5b);
				free(ip);
				app_thread_exit(1, net_fd);
			}

			free(ip);
		}
		else {
			log_message("Unsupported mode");
		}
		break;
	}
	}

	app_socket_pipe(inet_fd, net_fd);
	close(inet_fd);
	app_thread_exit(0, net_fd);

	return NULL;
}

int app_loop()
{
	int sock_fd, net_fd;
	int optval = 1;
	struct sockaddr_in local, remote;
	socklen_t remotelen;
	if ((sock_fd = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
		log_message("socket()");
		exit(1);
	}

	if (setsockopt
	(sock_fd, SOL_SOCKET, SO_REUSEADDR, (char*)&optval,
		sizeof(optval)) < 0) {
		/*
		* int setsockopt(SOCKET s, int level, int optname, const char *optval, int optlen);
		* s标识套接字的描述符
		* level定义选项的级别
		* optname要为其设置值得套接字选项
		* optval指向缓冲区的指针，在缓冲区中指定了所请求选项的值
		* optlen optval参数指向的缓冲区大小
		*/
		log_message("setsockopt()");
		exit(1);
	}

	memset(&local, 0, sizeof(local));
	local.sin_family = AF_INET;
	local.sin_addr.s_addr = htonl(INADDR_ANY);
	local.sin_port = htons(port);

	if (bind(sock_fd, (struct sockaddr*)&local, sizeof(local)) < 0) {
		log_message("bind()");
		exit(1);
	}

	if (listen(sock_fd, 25) < 0) {
		log_message("listen()");
		exit(1);
	}

	remotelen = sizeof(remote);
	memset(&remote, 0, sizeof(remote));

	log_message("Listening port %d...", port);

	pthread_t worker;
	while (1) {
		if ((net_fd =
			accept(sock_fd, (struct sockaddr*)&remote,
				&remotelen)) < 0) {
			log_message("accept()");
			exit(1);
		}
		int one = 1;
		setsockopt(sock_fd, SOL_TCP, TCP_NODELAY, &one, sizeof(one));
		if (pthread_create
		(&worker, NULL, &app_thread_process,
			(void*)&net_fd) == 0) {
			pthread_detach(worker);
		}
		else {
			log_message("pthread_create()");
		}
	}
}

void daemonize()
{
	pid_t pid;
	int x;

	pid = fork();

	if (pid < 0) {
		exit(EXIT_FAILURE);
	}

	if (pid > 0) {
		exit(EXIT_SUCCESS);
	}

	if (setsid() < 0) {
		exit(EXIT_FAILURE);
	}

	signal(SIGCHLD, SIG_IGN);
	signal(SIGHUP, SIG_IGN);

	pid = fork();

	if (pid < 0) {
		exit(EXIT_FAILURE);
	}

	if (pid > 0) {
		exit(EXIT_SUCCESS);
	}

	umask(0);
	chdir("/");

	for (x = sysconf(_SC_OPEN_MAX); x >= 0; x--) {
		close(x);
	}
}

void usage(char* app)
{
	printf
	("USAGE: %s [-h][-n PORT][-a AUTHTYPE][-u USERNAME][-p PASSWORD][-l LOGFILE]\n",
		app);
	printf("AUTHTYPE: 0 for NOAUTH, 2 for USERPASS\n");
	printf
	("By default: port is 1080, authtype is no auth, logfile is stdout\n");
	exit(1);
}

int main(int argc, char* argv[])
{
	int ret;
	log_file = stdout;
	auth_type = NOAUTH;
	arg_username = "user";
	arg_password = "pass";
	pthread_mutex_init(&lock, NULL); // 互斥锁

	signal(SIGPIPE, SIG_IGN); // 设置signal信号

	while ((ret = getopt(argc, argv, "n:u:p:l:a:hd")) != -1) {
		switch (ret) {
		case 'd': {
			daemon_mode = 1;
			daemonize();
			break;
		}
				// 监听信号端口
		case 'n': {
			port = atoi(optarg) & 0xffff;
			break;
		}
				// 设置用户名
		case 'u': {
			arg_username = strdup(optarg);
			break;
		}
				// 设置密码
		case 'p': {
			arg_password = strdup(optarg);
			break;
		}
				// 设置日志文件
		case 'l': {
			freopen(optarg, "wa", log_file);
			break;
		}
				// 设置auth_type
		case 'a': {
			auth_type = atoi(optarg);
			break;
		}
		case 'h':
		default:
			usage(argv[0]);
		}
	}
	// 日志输出
	log_message("Starting with authtype %X", auth_type);
	if (auth_type != NOAUTH) {
		log_message("Username is %s, password is %s", arg_username,
			arg_password);
	}
	// 循环调用软件
	app_loop();
	return 0;
}