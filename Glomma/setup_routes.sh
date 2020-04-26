for host in "mlc1" "mlc2" "mlc3" "mlc4"
do
    sudo ip route add `dig +short $host` via 192.168.1.1 dev eno2
    sudo ip route show match `dig +short $host`
done