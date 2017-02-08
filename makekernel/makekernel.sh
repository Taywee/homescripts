#!/bin/sh

usage() {
    cat <<USAGE
    $0 [options]

    -h          this help menu
    -r          reboot
USAGE
}

after() { :; }

while getopts 'chr' arg; do
    case "$arg" in
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

make -j10 && make modules_install && make install && genkernel --lvm --luks --busybox initramfs && grub-mkconfig -o /boot/grub/grub.cfg && emerge @module-rebuild && after
