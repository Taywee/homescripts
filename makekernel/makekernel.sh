#!/bin/sh

usage() {
    cat <<USAGE
    $0 [options]

    -c          use ccache
    -h          this help menu
    -r          reboot
USAGE
}

after() { :; }

while getopts 'chr' arg; do
    case "$arg" in
        c)
            export CCACHE_DIR=/var/tmp/ccache
            ;;
        h)
            usage
            exit 0
            ;;
        r)
            after() { reboot; }
            ;;
        *)
            usage
            exit 1
            ;;
    esac
done

if [ -n "$CCACHE_DIR" ]; then
    export PATH="/usr/lib64/ccache/bin:$PATH"
    export CC='ccache gcc'
    export CXX='ccache g++'
fi

make -j10 && make modules_install && make install && genkernel --lvm --luks --busybox initramfs && grub-mkconfig -o /boot/grub/grub.cfg && emerge @module-rebuild && after
