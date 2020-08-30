git clone --recursive https://github.com/cloudflare/quiche
cd quiche
cargo build --release --features pkg-config-meta,qlog
mkdir deps/boringssl/src/lib
ln -vnf $(find target/release -name libcrypto.a -o -name libssl.a) deps/boringssl/src/lib/