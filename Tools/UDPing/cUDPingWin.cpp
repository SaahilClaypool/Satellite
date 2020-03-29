// cUDPingWin.cpp (V1.0): the client of UDPing in MS windows.
//
// Author:  Huahui Wu
//          flashine@gmail.com
//
// History
//   Version 1.0 - 2005 Mar 08
//
// Description:
//	 cUDPingWin.cpp
//		Very simple, Works in conjunction with sUDPingWin.cpp 
//		(a Windows server) or sUDPingLnx (a Linux server).
//		The program attempts to connect to the server and port
//		specified on the command line. The client keeps sending 
//		packets to the server and receiving the bounced packets 
//		from server and calculating the time difference.
//	 XGetopt.h XGetopt.cpp
//		Hans Dietrich's implementation of getopt(), a function 
//		to parse command lines. Check the code for more details 		
//
// Compile and Link: 
//	 Use MS Visual C++ .NET
//	 Compile and link with wsock32.lib
//
// Run (Usage): 
//		cUDPingWin -p portnumber -h hostname 
//			-s packet_size_in_bytes -n packet_number_per_second
//		where the default values are:
//			hostname	: localhost		
//			portnumber	:	7979
//			packet_size	:	16
//			packet_number:	5
//
// License: 
//   This software is released into the public domain.
//   You are free to use it in any way you like.
//   This software is provided "as is" with no expressed
//   or implied warranty.  I accept no liability for any
//   damage or loss of business that this software may cause.
//
//

#include "stdafx.h"
#include <stdio.h>
#include <string.h>
#include <winsock.h>
#include <signal.h>
#include "XGetopt.h"

#define MAX_PKT_SIZE 4096
#define MAX_PKT_NUM 100

struct Ping_Pkt{
	int seq;
	LARGE_INTEGER counter;
	unsigned char padding[MAX_PKT_SIZE];
};

//global variables
int pkt_sent=0, pkt_rcvd=0;
double p; //loss rate
int rtt_min = 2000, rtt_max = 0;
double rtt_avg = 0;
char* nmServer; //server name
short nPort; //port number
short sPkt;  //packet size in bytes
short nPkt;  //packet number per second
LARGE_INTEGER initCounter; // the counter when PING starts


// Function prototype
void DatagramClient(char *szServer, short nPort);
DWORD WINAPI SendFunc( LPVOID lpParam ); 
void CleanUp(int);

LPHOSTENT lpHostEntry;
SOCKET	theSocket;
SOCKADDR_IN saServer;


// Helper macro for displaying errors
#define PRINTERROR(s)	\
		fprintf(stderr,"\n%s: %d\n", s, WSAGetLastError())

////////////////////////////////////////////////////////////

void main(int argc, char **argv)
{
	WORD wVersionRequested = MAKEWORD(1,1);
	WSADATA wsaData;
	int nRet;

	//use getopt to parse the command line
	// > cUDPingWin.exe -p portnumber -h hostname -s packet_size_in_bytes -n packet_number_per_second
	// where the default values are:
	//		portnumber	:	7979
	//		packet_size	:	16
	//		packet_number:	5
	int c;
	nmServer="localhost";
	nPort = 7979; //port number
	sPkt = 16;  //packet size in bytes
	nPkt = 5;  //packet number per second

	while ((c = getopt(argc, argv, _T("p:h:s:n:"))) != EOF)
    {
		switch (c)
        {
			case _T('p'):
				printf("portnumber: %d\n", atoi(optarg));
				nPort = atoi(optarg);
                break;

            case _T('h'):
				printf("hostname: %s\n", optarg);
				nmServer = optarg;
                break;

            case _T('s'):
				printf("packet size: %d\n", atoi(optarg));
                sPkt = atoi(optarg);
				if (sPkt > MAX_PKT_SIZE)
					sPkt = MAX_PKT_SIZE;
				break;

			case _T('n'):
                printf("packet number per second: %d\n", atoi(optarg));
                nPkt = atoi(optarg);
				if (nPkt > MAX_PKT_NUM)
					nPkt = MAX_PKT_NUM;
				break;

            case _T('?'):
	            printf("ERROR: illegal option %s\n", argv[optind-1]);
				printf("Usage:\n");
				printf("\t%s -p portnumber -h hostname -s packet_size_in_bytes -n packet_number_per_second\n", argv[0]);
				exit(1); 
				break;

            default:
                printf("WARNING: no handler for option %c\n", c);
				printf("Usage:\n");
				printf("\t%s -p portnumber -h hostname -s packet_size_in_bytes -n packet_number_per_second\n", argv[0]);
                exit(1);
                break;
        }
    }

	printf("Usage:\n");
	printf("\t%s -p portnumber -h hostname -s packet_size_in_bytes -n packet_number_per_second\n", argv[0]);

	//
	// Initialize WinSock and check the version
	//
	nRet = WSAStartup(wVersionRequested, &wsaData);
	if (wsaData.wVersion != wVersionRequested)
	{	
		fprintf(stderr,"\n Wrong version\n");
		return;
	}

	//
	// Go do all the stuff a datagram client does
	//
	signal(SIGINT, CleanUp);
	DatagramClient(nmServer, nPort);
	
	//
	// Release WinSock
	//
	WSACleanup();
}

////////////////////////////////////////////////////////////

void DatagramClient(char *szServer, short nPort)
{

	printf("Pinging %s with 32 bytes of data:\n\n", szServer);	

	//
	// Find the server
	//

	lpHostEntry = gethostbyname(szServer);
    if (lpHostEntry == NULL)
    {
        PRINTERROR("gethostbyname()");
        return;
    }


	//
	// Create a UDP/IP datagram socket
	//
	theSocket = socket(AF_INET,			// Address family
					   SOCK_DGRAM,		// Socket type
					   IPPROTO_UDP);	// Protocol
	if (theSocket == INVALID_SOCKET)
	{
		PRINTERROR("socket()");
		return;
	}

	//
	// Fill in the address structure for the server
	//
	saServer.sin_family = AF_INET;
	saServer.sin_addr = *((LPIN_ADDR)*lpHostEntry->h_addr_list);
										// ^ Server's address
	saServer.sin_port = htons(nPort);	// Port number from command line

   	Ping_Pkt ping_pkt; 
	int nRet;


	ping_pkt.seq = 0;

	::QueryPerformanceCounter(&initCounter);
	ping_pkt.counter = initCounter;

	//send the first packet to setup the socket
	pkt_sent = 1;
	nRet = sendto(theSocket,				// Socket
				  (const char*)&ping_pkt,	// Data buffer
				  sPkt,			// Length of data
				  0,						// Flags
				  (LPSOCKADDR)&saServer,	// Server address
				sizeof(struct sockaddr)); // Length of address
	if (nRet == SOCKET_ERROR)
	{
		PRINTERROR("sendto()");
		closesocket(theSocket);
		return;
	}	//

    DWORD dwThreadId, dwThrdParam = 1; 
    HANDLE hThread; 

    hThread = CreateThread( 
        NULL,                        // default security attributes 
        0,                           // use default stack size  
        SendFunc,                  // thread function 
        &dwThrdParam,                // argument to thread function 
        0,                           // use default creation flags 
        &dwThreadId);                // returns the thread identifier 
 
   // Check the return value for success. 
   if (hThread == NULL) 
   {
      printf( "CreateThread failed (%d)\n", GetLastError() ); 
   }

	// Wait for the reply
	//
	memset(&ping_pkt, 0, sizeof(Ping_Pkt));
	int nFromLen;
	int rtt;
	int tSent; // the time when each packet was sent in millisecond
	LARGE_INTEGER curCounter;
	LARGE_INTEGER   frequency;


	while(1){
		nFromLen = sizeof(struct sockaddr);
		nRet = recvfrom(theSocket,						// Socket
			 (char*)&ping_pkt,						// Receive buffer
			 sPkt,					// Length of receive buffer
			 0,								// Flags
			 (LPSOCKADDR)&saServer,			// Buffer to receive sender's address
			 &nFromLen);					// Length of address buffer
		if (nRet == SOCKET_ERROR)
		{
			PRINTERROR("recvfrom()");
			closesocket(theSocket);
			return;
		}

		pkt_rcvd ++;


		//get cpu frequency and current counter
		::QueryPerformanceFrequency(&frequency);
		::QueryPerformanceCounter(&curCounter);

		//get rtt in millisecond
		rtt =(int)((((double)(curCounter.QuadPart - ping_pkt.counter.QuadPart)/(double)
		      frequency.QuadPart)*1000.0)+0.5);

		//get tSent in millisecond
		tSent = (int)((((double)(ping_pkt.counter.QuadPart - initCounter.QuadPart)/(double)
		      frequency.QuadPart)*1000.0)+0.5);
 
		if (rtt < rtt_min){
			rtt_min = rtt;
		}
		if (rtt > rtt_max){
			rtt_max = rtt;
		}

		rtt_avg = ((pkt_rcvd - 1) * rtt_avg + rtt) / pkt_rcvd;
		//
		// Display the data that was received
		//
		printf("Reply from %s: bytes=%d rtt=%dms seq=%d tSent=%dms\n",
			nmServer, sPkt, rtt, ping_pkt.seq, tSent);
	}

	CloseHandle( hThread );

	closesocket(theSocket);
	return;
}


DWORD WINAPI SendFunc( LPVOID lpParam ) 
{ 
	// Send data to the server
	//
	Ping_Pkt ping_pkt; 
	int nRet;

	for (int i =1; ; i ++){
		ping_pkt.seq = i;
		::QueryPerformanceCounter(&ping_pkt.counter);

		pkt_sent ++;
		nRet = sendto(theSocket,				// Socket
					  (const char*)&ping_pkt,	// Data buffer
					  sPkt,			// Length of data
					  0,						// Flags
					  (LPSOCKADDR)&saServer,	// Server address
					sizeof(struct sockaddr)); // Length of address
		if (nRet == SOCKET_ERROR)
		{
			PRINTERROR("sendto()");
			closesocket(theSocket);
			return 0;
		}
		::Sleep(1000/nPkt);
	}
	 return 0; 
} 

void CleanUp(int arg1){
	p = (100.0 * (pkt_sent-pkt_rcvd)) / pkt_sent;
	printf("Ping statistics for %s:\n", nmServer);
	printf("\tPackets: Sent = %d, Received = %d, Lost = %d (%6.2f %%loss),\n", 
			pkt_sent, pkt_rcvd, pkt_sent-pkt_rcvd, p);
	printf("Approximate round trip times in milli-seconds:\n");
	printf("\tMinimum = %dms, Maximum = %dms, Average = %6.2fms\n", rtt_min, rtt_max, rtt_avg);
	exit(0);
}
