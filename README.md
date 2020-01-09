Python 3 Android
================

This is an experimental set of build scripts that will cross-compile the latest Python 3 git master for an Android device.

Build status:

| System            | Status        |
| ----------------- |---------------|
| Linux (GitLab)    | [![Build Status](https://gitlab.com/yan12125/python3-android/badges/master/pipeline.svg)](https://gitlab.com/yan12125/python3-android/pipelines) |

Prerequisites
-------------

Building requires:

1. Linux. This project might work on other Unix-like systems but no guarantee.
2. Android NDK r19 beta 1 or newer installed and environment variable ``$ANDROID_NDK`` points to its root directory. NDk r18 or below is not supported.

Running requires:

1. Android 5.0 (Lollipop, API 21) or above
2. arm, arm64, x86 or x86-64

Build
-----

```
# CPython requires explicit --build
CONFIG_SITE="$PWD/Android/config.site" ./configure \
    --prefix=/usr --enable-shared --host=armv7a-linux-androideabi --build=x86_64-linux-gnu --disable-ipv6
```

Installation
------------

1. Make sure `adb shell` works fine
2. Copy all files in it to a folder on the device (e.g., ```/data/local/tmp/python3```). Note that on most devices `/sdcard` is not on a POSIX-compliant filesystem, so the python binary will not run from there.
3. In adb shell:
<pre>
cd /data/local/tmp
. ./python3/tools/env.sh
python3.9
</pre>
   And have fun!

SSL/TLS
-------
SSL certificates have old and new naming schemes. Android uses the old scheme yet the latest OpenSSL uses the new one. If you got ```CERTIFICATE_VERIFY_FAILED``` when using SSL/TLS in Python, you need to generating certificate names of the new scheme:
```
python3.9 ./python3/tools/c_rehash.py
```
Check SSL/TLS functionality with:
```
python3.9 ./python3/tools/ssl_test.py
```
