// sUDPingLnx.cpp (V1.0): the server of UDPing in Linux.
//
// Author:  Huahui Wu
//          flashine@gmail.com
//
// History
//   Version 1.0 - 2005 Mar 08
//
// Description:
//   sUDPingLnx.cpp
//		Very simple, Works in conjunction with cUDPingWin.cpp as 
//		a Windows client or cUDPingLnx as a Linux client.
//		The program sets itself up as a server using the UDP
//		protocol. It waits for UDP data from a client, displays
//		the incoming connection, bounce the ping packet back 
//		to the client.
//
// Compile and Link: 
//	 g++ sUDPingLnx.cpp -o sUDPingLnx
//
// Run: 
//   Pass the port number that the server should bind() to
//   on the command line. Any port number not already in use
//   can be specified. Example: sUDPingLnx 7979
//
// License: 
//   This software is released into the public domain.
//   You are free to use it in any way you like.
//   This software is provided "as is" with no expressed
//   or implied warranty.  I accept no liability for any
//   damage or loss of business that this software may cause.
//
///////////////////////////////////////////////////////////////////////////////

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <netdb.h>
#include <signal.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>


//global variables
int theSocket;

// Function prototype
void DatagramServer(short nPort);	// the server 
void CleanUp(int);		     // press ctrl_c to cleanup	

int main(int argc, char **argv)
{
	int nRet;
	short nPort;

	//
	// Check for port argument
	//
	if (argc == 2)
	  nPort = atoi(argv[1]);
	else
	  nPort = 7979;
	
	signal(SIGINT, CleanUp);
	//
	// Do all the stuff a datagram server does
	//
	DatagramServer(nPort);
	
	return (0);	
}

////////////////////////////////////////////////////////////

void DatagramServer(short nPort)
{
	//
	// Create a UDP/IP datagram socket
	//
	if ((theSocket = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
	  perror("can't open stream socket");
	  exit(1);
	}

	// Fill in the address structure
	//
	struct sockaddr_in saServer;
	bzero((char *) &saServer, sizeof(saServer));
	saServer.sin_family = AF_INET;
	saServer.sin_addr.s_addr 
	  = htonl(INADDR_ANY); // Let socket assign address
	saServer.sin_port = htons(nPort); // Use port passed from user


	//
	// bind the name to the socket
	//
	int nRet;
	nRet = bind(theSocket,		// Socket descriptor
		    (struct sockaddr *)&saServer,  // Address to bind to
		    sizeof(saServer)	// Size of address
		    );
	if (nRet < 0)	{
	  perror("Can't bind to local address");
	  exit(1);
	}


	//
	// This isn't normally done or required, but in this 
	// example we're printing out where the server is waiting
	// so that you can connect the example client.
	//
	int nLen;
	nLen = sizeof(sockaddr);
	char szBuf[4096];

	nRet = gethostname(szBuf, sizeof(szBuf));
	if (nRet < 0)
	{
	  perror("gethostname");
	  exit(1);
	}

	//
	// Show the server name and port number
	//
	printf("\nServer named %s waiting on port %d\n",
			szBuf, nPort);
			

	//
	// Wait for data from the client
	//
	struct sockaddr_in saClient;

	while(1){
	  memset(szBuf, 0, sizeof(szBuf));
	  nRet = recvfrom(theSocket,  // Bound socket
			  szBuf,      // Receive buffer
			  sizeof(szBuf),// Size of buffer in bytes
			  0, // Flags
			  (struct sockaddr *)&saClient,// Buffer
			  (socklen_t *)&nLen); // Length of client address

		//
		// Show that we've received some data
		//
		printf("\n%d bytes received\n", nRet);

		//
		// Send data back to the client
		//
		sendto(theSocket,  // socket
			szBuf,	   // Send buffer
			nRet,	   // Length of data to be sent
			0,         // Flags
			(struct sockaddr *)&saClient, // Address to send
			nLen);	   // Length of address

	}
	return;
}

void CleanUp(int arg1){
        close(theSocket);
	printf("Server is now off\n");
	exit(0);
}
