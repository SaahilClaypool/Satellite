#!/usr/bin/python3
# Main script to generate a trial
import command as cmd
import time

BDP = 65625000

cmd.MOCK = True

class Tc:
    def __init__(self, cc='cubic', win=BDP, host=""):
        self.cc = cc
        self.win = BDP
        self.host = host
        self.time = 90

    def cmd(self):
        win, cc = self.win, self.cc
        command = ' && '.join([
            f"sudo sysctl -w net.ipv4.tcp_mem='{win} {win} {win}'",
            f"sudo sysctl -w net.ipv4.tcp_wmem='{win} {win} {win}'",
            f"sudo sysctl -w net.ipv4.tcp_rmem='{win} {win} {win}'",
            f"sudo sysctl -w net.ipv4.tcp_congestion_control='{cc}'"])
        
        return command

    def setup_tc(self):
        cmd.run_command(self.cmd(), host=self.host)

def sleep(seconds=1):
    if cmd.MOCK:
        print(f'would sleep for {seconds}s')
    else:
        time.sleep(seconds)


class Trial:
    time = 90
    def __init__(self, name='experiment', dir='.', local='glomma', remote='mlc1.cs.wpi.edu'):
        self.name = name
        self.dir = dir
        self.cc = 'cubic'
        self.remote = remote
        self._local_tc = Tc()
        self._remote_tc = Tc()

    def local_tc(self, cc='cubic', win=BDP):
        self._local_tc = Tc(cc, win)

    def remote_tc(self, cc='cubic', win=BDP):
        self._remote_tc = Tc(cc, win, self.remote)

    def _setup_tc(self):
        self._local_tc.setup_tc()
        self._remote_tc.setup_tc()


    def _start_udp_ping(self):
        remote_cmd = "~/.local/bin/sUDPingLnx &"
        cmd.run_command(remote_cmd, host=self.remote)

        sleep()

        local_cmd = f"cUDPingLnx -h {self.remote}"
        cmd.run_command(local_cmd)

    def _cleanup(self):
        procs = ['tcpdump', 'cUDPingLnx', 'sUDPingLnx', 'iperf3']
        kill_cmd = 'pkill '+ '; pkill '.join(procs) + ';'
        cmd.run_command(kill_cmd).wait()
        cmd.run_command(kill_cmd, host=self.remote).wait()

    def _start_iperf(self, remote_sender=True):
        reverse = "--reverse" if remote_sender else ""
        iperf_server = f"iperf3 --server"
        local_iperf = f"iperf3 -c {self.remote} {reverse} -t {self.time} -p 5201"
        cmd.run_command(iperf_server, host=self.remote).wait()
        cmd.run_command(local_iperf).wait()

    def start_tcpdump(self):
        pass


    def start(self, time=-1):
        """
        2. starts iperf server on remote
        3. starts tcpdump
        4. starts iperf client on local 
        6. copies captures locally
        """
        self.time = time if time != -1 else self.time
        cmd.clear()
        self._setup_tc()
        self._start_udp_ping()
        self._start_iperf()

        self._cleanup()
        cmd.dump()

    @staticmethod
    def mock(t=True):
        cmd.MOCK = t


