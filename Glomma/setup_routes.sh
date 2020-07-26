# for host in "mlc1" "mlc2" "mlc3" "mlc4"
for host in "mlcnetA.cs.wpi.edu" "mlcnetB.cs.wpi.edu" "mlcnetC.cs.wpi.edu" "mlcnetD.cs.wpi.edu"
do
    sudo ip route add `dig +short $host` via 192.168.1.1 dev eno2
    sudo ip route show match `dig +short $host`
done


sudo ip route add 192.168.100.0/24 dev eno2
