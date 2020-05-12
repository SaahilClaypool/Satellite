#!/usr/bin/python3
# Main script to generate a trial
import command as cmd
import time
import os

BDP = 65625000

cmd.MOCK = True

# TODO: all machines seem to use the same interface name, so we don't need this
devices = {
    "mlc1": "ens3",
    "mlc2": "ens3",
    "mlc3": "ens3",
}

REMOTE_DEVICE = "ens3"
LOCAL_DEVICE = "eno2"


class Tc:
    def __init__(self, cc='cubic', win=BDP, host=""):
        self.cc = cc
        self.win = BDP
        self.host = host
        self.time = 90
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
        cmd.run(self.cmd(), host=self.host)


def sleep(seconds=1):
    if cmd.MOCK:
        print(f'would sleep for {seconds}s')
    else:
        time.sleep(seconds)


class Trial:
    time = 90

    def __init__(self, name='experiment', dir='.', local='glomma', remote='mlc1', data=None, timeout=10 * 60):
        """
        args:
            data: string of the number of bytes we should send. Ex. 1G
        """
        self.name = name
        self.dir = dir
        self.cc = 'cubic'
        self.remote = remote
        self._local_tc = Tc()
        self._remote_tc = Tc(host=remote)
        self.local_pcap = f"{self.data_dir()}/local.pcap"
        self.remote_pcap = f"./{self.data_dir()}/{self.remote}.pcap"
        self.data = data
        self._mock = False
        self._timeout = timeout

    def local_tc(self, cc='cubic', win=BDP):
        self._local_tc = Tc(cc, win)

    def remote_tc(self, cc='cubic', win=BDP):
        self._remote_tc = Tc(cc, win, self.remote)

    def _setup_tc(self):
        self._local_tc.setup_tc()
        self._remote_tc.setup_tc()

    def _start_udp_ping(self):
        remote_cmd = "~/.local/bin/sUDPingLnx"
        cmd.run(remote_cmd, host=self.remote).wait(self._timeout)

        sleep()

        local_cmd = f"cUDPingLnx -h {self.remote}"
        cmd.run(local_cmd)

    def _cleanup(self):
        procs = ['tcpdump', 'cUDPingLnx', 'sUDPingLnx', 'iperf3']
        kill_cmd = 'pkill ' + '; pkill '.join(procs) + ';'
        cmd.run(kill_cmd).wait(self._timeout)
        cmd.run(kill_cmd, host=self.remote).wait(self._timeout)

    def _start_iperf(self, remote_sender=True):
        reverse = "--reverse" if remote_sender else ""
        iperf_server = f"iperf3 --server"
        amount = f"-t {self.time}" if not self.data else f"-n {self.data}"
        local_iperf = f"iperf3 -c {self.remote} {reverse} {amount} -p 5201"
        cmd.run(iperf_server, host=self.remote).wait(self._timeout)
        cmd.run(local_iperf).wait(self._timeout)

    def data_dir(self):
        dir = f"./data/{self.name}"
        if not os.path.exists(dir):
            os.makedirs(dir)
        return dir

    def _start_tcpdump(self):
        local = f"sudo tcpdump -Z $USER -i {LOCAL_DEVICE} -s 96 port 5201 -w {self.local_pcap}"
        remote = f"sudo tcpdump -Z $USER -i {REMOTE_DEVICE} -s 96 port 5201 -w pcap.pcap"
        cmd.run(remote, host=self.remote).wait(self._timeout)
        cmd.run(local)
        sleep(5)

    def _copy_remote_pcap(self):
        command = f"scp {self.remote}:pcap.pcap {self.remote_pcap}"
        cmd.run(command).wait(self._timeout)

    def start(self, time=-1):
        """
        2. starts iperf server on remote
        3. starts tcpdump
        4. starts iperf client on local 
        6. copies captures locally

        returns: [local_pcap, remote_pcap]
        """
        try:
            self.mock(self._mock)
            self.time = time if time != -1 else self.time
            cmd.clear()
            self._cleanup()

            self._setup_tc()
            self._start_udp_ping()
            self._start_tcpdump()

            self._start_iperf()

            self._cleanup()
            self._copy_remote_pcap()
            cmd.dump()
            return [self.local_pcap, self.remote_pcap]
        except:
            print(f"ERROR: failed to finish experiemnt for directory {self.dir}")
            self._cleanup()
        finally:
            print(f"finished with {self.dir}")

    def get_pcaps(self):
        return [self.local_pcap, self.remote_pcap]

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
