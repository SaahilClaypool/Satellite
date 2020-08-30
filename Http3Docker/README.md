# HTTP3 dockerfile

```
sudo docker build -t saahil/quic .
sudo docker run -p 1001:443/udp -d -t saahil/quic
sudo docker run --network host -t saahil/quic curl --insecure  --http3 https://127.0.0.1:1001/test
sudo docker run --network host -t saahil/quic curl --insecure  --http3 https://quic.tech:8443/
curl --insecure --http3 https://127.0.0.1:1001/test
```