git clone https://github.com/curl/curl
cd curl
./buildconf
./configure LDFLAGS="-Wl,-rpath,$PWD/../quiche/target/release" --with-ssl=$PWD/../quiche/deps/boringssl/src --with-quiche=$PWD/../quiche/target/release --enable-alt-svc
make

ln -sf `pwd`/src/curl /app/bin