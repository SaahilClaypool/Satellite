// cUDPingLnx.cpp (V1.0): the client of UDPing in Linux
//
// Author:  Huahui Wu
//          flashine@gmail.com
//
// History
//   Version 1.0 - 2005 Mar 08
//
// Description:
//	 cUDPingLnx.cpp
//		Very simple, Works in conjunction with sUDPingWin.cpp 
//		(a Windows server) or sUDPingLnx (a Linux server).
//		The program attempts to connect to the server and port
//		specified on the command line. The client keeps sending 
//		packets to the server and receiving the bounced packets 
//		from server and calculating the time difference.
//
// Compile and Link: 
//	 g++ cUDPingLnx.cpp -o cUDPingLnx -lpthread
//
// Run (Usage): 
//		cUDPingLnx -p portnumber -h hostname 
//			-s packet_size_in_bytes -n packet_number_per_second
//		where the default values are:
//			hostname	: localhost		
//			portnumber	:	7979
//			packet_size	:	12
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


#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include <unistd.h>
#include <netdb.h>
#include <pthread.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#ifndef INADDR_NONE
#define INADDR_NONE 0xffffffff /* should be in <netinet/in.h> */
#endif


#define MAX_PKT_SIZE 4096
#define MAX_PKT_NUM 100

struct Ping_Pkt{
	int seq;
	struct timeval tv;
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
struct timeval initTv; // the timeval when PING starts 

// Function prototype
void DatagramClient(char *szServer, short nPort);
void *SendFunc(void *); 
void CleanUp(int);

int	theSocket;
struct sockaddr_in saServer;


////////////////////////////////////////////////////////////

int main(int argc, char **argv)
{
  int nRet;
  
  //use getopt to parse the command line
  // > cUDPingLnx -p portnumber -h hostname -s packet_size_in_bytes -n packet_number_per_second
  // where the default values are:
  //		portnumber	:	7979
  //		packet_size	:	16
  //		packet_number:	5
  int c;
  nmServer="localhost";
  nPort = 7979; //port number
  sPkt = sizeof(int)+sizeof(timeval);  //minimum packet size in bytes
  nPkt = 5;  //packet number per second
  
  while ((c = getopt(argc, argv, "p:h:s:n:")) != EOF)
    {
      switch (c)
        {
	case 'p':
	  printf("portnumber: %d\n", atoi(optarg));
	  nPort = atoi(optarg);
	  break;
	  
	case 'h':
	  printf("hostname: %s\n", optarg);
	  nmServer = optarg;
	  break;
	  
	case 's':
	  printf("packet size: %d\n", atoi(optarg));
	  sPkt = atoi(optarg);
	  if (sPkt > MAX_PKT_SIZE)
	    sPkt = MAX_PKT_SIZE;
	  break;
	  
	case 'n':
	  printf("packet number per second: %d\n", atoi(optarg));
	  nPkt = atoi(optarg);
	  if (nPkt > MAX_PKT_NUM)
	    nPkt = MAX_PKT_NUM;
	  break;
	  
	case '?':
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
  // Go do all the stuff a datagram client does
  //
  signal(SIGINT, CleanUp);
  DatagramClient(nmServer, nPort);
  
}

////////////////////////////////////////////////////////////

void DatagramClient(char *szServer, short nPort)
{
  struct hostent *hp;

  printf("Pinging %s with %d bytes of data:\n\n", szServer, sPkt); 
  
  //
  // Find the server
  //
  // Convert the host name as a dotted-decimal number.

   bzero((void *) &saServer, sizeof(saServer));
   printf("Looking up %s...\n", szServer);
   if ((hp = gethostbyname(szServer)) == NULL) {
     perror("host name error");
     exit(1);
   }
   bcopy(hp->h_addr, (char *) &saServer.sin_addr, hp->h_length);

   //
   // Create a UDP/IP datagram socket
   //
   theSocket = socket(AF_INET,			// Address family
		      SOCK_DGRAM,		// Socket type
		      IPPROTO_UDP);	// Protocol
   if (theSocket < 0){
       perror("Failed in creating socket");
       exit(1);
   }
   
   //
   // Fill in the address structure for the server
   //
   saServer.sin_family = AF_INET;
   saServer.sin_port = htons(nPort);	// Port number from command line

   Ping_Pkt ping_pkt; 
   int nRet;

   ping_pkt.seq = 0; //prepare the first packet

   gettimeofday(&initTv, NULL);
   ping_pkt.tv = initTv;

   //send the first packet to setup the socket
   pkt_sent = 1;
   nRet = sendto(theSocket,		// Socket
		 (const char*)&ping_pkt,// Data buffer
		 sPkt,			// Length of data
		 0,			// Flags
		 (struct sockaddr *)&saServer,	// Server address
		 sizeof(struct sockaddr)); // Length of address
   if (nRet < 0 ){
       perror("sending");
       close(theSocket);
       exit(1);
   } 

   pthread_t idA, idB; /* ids of threads */
   void *MyThread(void *);
   
   if (pthread_create(&idA, NULL, SendFunc, (void *)"Send") != 0) {
     perror("pthread_create");
     exit(1);
   }
 
   // Wait for the first reply
   //
   memset(&ping_pkt, 0, sizeof(Ping_Pkt));

   int nFromLen;
   int rtt;
   int tSent; // the time when each packet was sent in millisecond
   struct timeval curTv;

   while(1){
     nFromLen = sizeof(struct sockaddr);
     nRet = recvfrom(theSocket,	// Socket
		     (char*)&ping_pkt, // Receive buffer
		     sPkt, // Length of receive buffer
		     0,	   // Flags
		     (struct sockaddr *)&saServer, // Sender's address
		     (socklen_t *)&nFromLen);  // Length of address buffer
     if (nRet < 0){
       perror("receiving");
       close(theSocket);
       exit(1);
     }

     pkt_rcvd ++;


     //get current tv
     gettimeofday(&curTv, NULL);

     //get rtt in millisecond
     rtt =(int)((curTv.tv_sec - ping_pkt.tv.tv_sec) * 1000 +
		+ (curTv.tv_usec - ping_pkt.tv.tv_usec)/1000 + 0.5);
     
     //get tSent in millisecond
     tSent =(int)((ping_pkt.tv.tv_sec - initTv.tv_sec) * 1000 +
		+ (ping_pkt.tv.tv_usec - initTv.tv_usec)/1000 + 0.5);

    long int system_time = (ping_pkt.tv.tv_sec * 1000) + (ping_pkt.tv.tv_usec / 1000 + 0.5);
 
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
     printf("Reply from %s: bytes=%d rtt=%dms seq=%d tSent=%dms systemTime=%ld\n",
	    nmServer, sPkt, rtt, ping_pkt.seq, tSent, system_time);
   }
   
   (void)pthread_join(idA, NULL);
   printf("The sending thread is finished\n");

   close(theSocket);
   return;
}


void *SendFunc(void *arg) 
{ 
  // Send data to the server
  //
  Ping_Pkt ping_pkt; 
  int nRet;
  
  for (int i =1; ; i ++){
    ping_pkt.seq = i;
    gettimeofday(&ping_pkt.tv, NULL);
    
    pkt_sent ++;
    nRet = sendto(theSocket,		// Socket
		  (const char*)&ping_pkt,	// Data buffer
		  sPkt,			// Length of data
		  0,			// Flags
		  (struct sockaddr *)&saServer,	// Server address
		  sizeof(struct sockaddr)); // Length of address
    if (nRet < 0)
      {
	perror("sending");
	close(theSocket);
	exit(1);
      }
    usleep(1000000/nPkt);
  }
} 

void CleanUp(int arg1){
  p = (100.0 * (pkt_sent-pkt_rcvd)) / pkt_sent;
  printf("Ping statistics for %s:\n", nmServer);
  printf("\tPackets: Sent = %d, Received = %d, Lost = %d (%6.2f %%loss),\n", pkt_sent, pkt_rcvd, pkt_sent-pkt_rcvd, p);
  printf("Approximate round trip times in milli-seconds:\n");
  printf("\tMinimum = %dms, Maximum = %dms, Average = %6.2fms\n", rtt_min, rtt_max, rtt_avg);
  close(theSocket);
  exit(0);
}
