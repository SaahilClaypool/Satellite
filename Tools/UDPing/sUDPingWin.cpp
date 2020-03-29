// sUDPingWin.cpp (V1.0): the server of UDPing in MS windows.
//
// Author:  Huahui Wu
//          flashine@gmail.com
//
// History
//   Version 1.0 - 2005 Mar 08
//
// Description:
//   sUDPingWin.cpp
//		Very simple, Works in conjunction with cUDPingWin.cpp as 
//		a Windows client or cUDPingLnx as a Linux client.
//		The program sets itself up as a server using the UDP
//		protocol. It waits for UDP data from a client, displays
//		the incoming connection, bounce the ping packet back 
//		to the client.
//
// Compile and Link: 
//	 Use MS Visual C++ .NET
//	 Compile and link with wsock32.lib
//
// Run: 
//   Pass the port number that the server should bind() to
//   on the command line. Any port number not already in use
//   can be specified. Example: sUDPingWin 2000
//
// License: 
//   This software is released into the public domain.
//   You are free to use it in any way you like.
//   This software is provided "as is" with no expressed
//   or implied warranty.  I accept no liability for any
//   damage or loss of business that this software may cause.
//
///////////////////////////////////////////////////////////////////////////////

#include "stdafx.h"
#include "winsock.h"
#include <signal.h>

// Function prototype
void DatagramServer(short nPort);	// the server 
void CleanUp(int);						// handle for ctrl_c	

// Helper macro for displaying errors
#define PRINTERROR(s)	\
		fprintf(stderr,"\n%: %d\n", s, WSAGetLastError())

void main(int argc, char **argv)
{
	WORD wVersionRequested = MAKEWORD(1,1);
	WSADATA wsaData;
	int nRet;
	short nPort;

	//
	// Check for port argument
	//
	if (argc != 2)
	{
		fprintf(stderr,"\nUsage: %s PortNumber\n", argv[0]);
		return;
	}

	nPort = atoi(argv[1]);
	
	//
	// Initialize WinSock and check version
	//
	nRet = WSAStartup(wVersionRequested, &wsaData);
	if (wsaData.wVersion != wVersionRequested)
	{	
		fprintf(stderr,"\n Wrong version\n");
		return;
	}


	signal(SIGINT, CleanUp);
	//
	// Do all the stuff a datagram server does
	//
	DatagramServer(nPort);
	
	//
	// Release WinSock
	//
	WSACleanup();
}

////////////////////////////////////////////////////////////

void DatagramServer(short nPort)
{
	//
	// Create a UDP/IP datagram socket
	//
	SOCKET theSocket;

	theSocket = socket(AF_INET,		// Address family
					   SOCK_DGRAM,  // Socket type
					   IPPROTO_UDP);// Protocol
	if (theSocket == INVALID_SOCKET)
	{
		PRINTERROR("socket()");
		return;
	}

	
	//
	// Fill in the address structure
	//
	SOCKADDR_IN saServer;

	saServer.sin_family = AF_INET;
	saServer.sin_addr.s_addr = INADDR_ANY; // Let WinSock assign address
	saServer.sin_port = htons(nPort);	   // Use port passed from user


	//
	// bind the name to the socket
	//
	int nRet;

	nRet = bind(theSocket,				// Socket descriptor
				(LPSOCKADDR)&saServer,  // Address to bind to
				sizeof(struct sockaddr)	// Size of address
				);
	if (nRet == SOCKET_ERROR)
	{
		PRINTERROR("bind()");
		closesocket(theSocket);
		return;
	}


	//
	// This isn't normally done or required, but in this 
	// example we're printing out where the server is waiting
	// so that you can connect the example client.
	//
	int nLen;
	nLen = sizeof(SOCKADDR);
	char szBuf[4096];

	nRet = gethostname(szBuf, sizeof(szBuf));
	if (nRet == SOCKET_ERROR)
	{
		PRINTERROR("gethostname()");
		closesocket(theSocket);
		return;
	}

	//
	// Show the server name and port number
	//
	printf("\nServer named %s waiting on port %d\n",
			szBuf, nPort);
			

	//
	// Wait for data from the client
	//
	SOCKADDR_IN saClient;

	while(1){
		memset(szBuf, 0, sizeof(szBuf));
		nRet = recvfrom(theSocket,				// Bound socket
						szBuf,					// Receive buffer
						sizeof(szBuf),			// Size of buffer in bytes
						0,						// Flags
						(LPSOCKADDR)&saClient,	// Buffer to receive client address 
						&nLen);					// Length of client address buffer

		//
		// Show that we've received some data
		//
		printf("\n%d bytes received\n", nRet);


		//
		// Send data back to the client
		//
		sendto(theSocket,					// socket
			szBuf,							// Send buffer
			nRet,							// Length of data to be sent
			0,								// Flags
			(LPSOCKADDR)&saClient,			// Address to send data to
			nLen);							// Length of address

	}
	closesocket(theSocket);
	return;
}

void CleanUp(int arg1){
	printf("Server is now off\n");
	exit(0);
}