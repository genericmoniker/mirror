# Deployment Testing

I was going to try to run Raspberry Pi OS Desktop in QEMU (since it supports
cross-architecture emulation), but I don't know what the heck I'm doing...

https://www.qemu.org/download/#windows

```
"/c/Program Files/qemu/qemu-system-aarch64" \
    -M virt \
    -cpu cortex-a57 \
    -m 4G \
    -drive file=2025-12-04-raspios-trixie-arm64.img,if=none,format=raw
```
