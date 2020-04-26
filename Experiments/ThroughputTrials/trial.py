#!/usr/bin/python3
# Main script to generate a trial
import command as cmd
import time
import os

BDP = 65625000

cmd.MOCK = True

MLC1_DEVICE = "ens3"
LOCAL_DEVICE = "eno2"


class Tc:
    def __init__(self, cc='cubic', win=BDP, host=""):
        self.cc = cc
        self.win = BDP
        self.host = host
        self.time = 90
        self.time = 90
        self._mock = False

    def cmd(self):
        win, cc = self.win, self.cc
        command = ' && '.join([
            f"sudo sysctl -w net.ipv4.tcp_mem='{win} {win} {win}'",
            f"sudo sysctl -w net.ipv4.tcp_wmem='{win} {win} {win}'",
            f"sudo sysctl -w net.ipv4.tcp_rmem='{win} {win} {win}'",
            f"sudo sysctl -w net.ipv4.tcp_congestion_control='{cc}'"])

        return command

    def setup_tc(self):
        cmd.run(self.cmd(), host=self.host)


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
        remote_cmd = "~/.local/bin/sUDPingLnx"
        cmd.run(remote_cmd, host=self.remote).wait()

        sleep()

        local_cmd = f"cUDPingLnx -h {self.remote}"
        cmd.run(local_cmd)

    def _cleanup(self):
        procs = ['tcpdump', 'cUDPingLnx', 'sUDPingLnx', 'iperf3']
        kill_cmd = 'pkill ' + '; pkill '.join(procs) + ';'
        cmd.run(kill_cmd).wait()
        cmd.run(kill_cmd, host=self.remote).wait()

    def _start_iperf(self, remote_sender=True):
        reverse = "--reverse" if remote_sender else ""
        iperf_server = f"iperf3 --server"
        local_iperf = f"iperf3 -c {self.remote} {reverse} -t {self.time} -p 5201"
        cmd.run(iperf_server, host=self.remote).wait()
        cmd.run(local_iperf).wait()

    def data_dir(self):
        dir = f"./data/{self.name}"
        if not os.path.exists(dir):
            os.makedirs(dir)
        return dir

    def _start_tcpdump(self):
        local = f"sudo tcpdump -Z $USER -i {LOCAL_DEVICE} -s 96 port 5201 -w {self.data_dir()}/local.pcap"
        remote = f"sudo tcpdump -Z $USER -i {MLC1_DEVICE} -s 96 port 5201 -w pcap.pcap"
        cmd.run(remote, host=self.remote).wait()
        cmd.run(local)
        sleep(5)

    def _copy_pcap(self):
        command = f"scp {self.remote}:pcap.pcap ./{self.data_dir()}/{self.remote}.pcap"
        cmd.run(command).wait()

    def start(self, time=-1):
        """
        2. starts iperf server on remote
        3. starts tcpdump
        4. starts iperf client on local 
        6. copies captures locally
        """
        self.mock(self._mock)
        self.time = time if time != -1 else self.time
        cmd.clear()
        self._cleanup()

        self._setup_tc()
        self._start_udp_ping()
        self._start_tcpdump()

        self._start_iperf()

        self._cleanup()
        self._copy_pcap()
        cmd.dump()

    def mock(self, t=True):
        self._mock = t
        cmd.MOCK = t

    @staticmethod
    def global_mock(t=True):
        cmd.MOCK = t


def main():
    # from trial import *
    t = Trial()
    t.mock()
    t.start()
