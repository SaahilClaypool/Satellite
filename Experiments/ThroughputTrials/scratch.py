from analyze import *
import summary as sm




pcaps = all_pcaps()
local, remote, dir = next(pcaps)

results = analyze(local, remote, dir)
local_sender = results[0]
local_sender_steady = results[1]
remote_sender = results[2]
remote_sender_steady = results[3]

throughput_quantiles, rtt_quantiles, host, protocol, start_time, _ = results[0]
rtt_quantiles