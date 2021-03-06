Python 3 Android
================

This is an experimental set of build scripts that will cross-compile the latest Python 3 git master for an Android device.

Prerequisites
-------------

Building requires:

1. Linux. This project might work on other Unix-like systems but no guarantee.
2. Android NDK r21 installed and environment variable ``$ANDROID_NDK`` points to its root directory. Older NDK may not work and NDK <= r18 is known to break.
3. git and python3.9 in $PATH. It's recommended to use the latest git-master to build python3.9. Here are some ways to install the python3.9:
* For Arch Linux users, install [python-git](https://aur.archlinux.org/packages/python-git) package from AUR
* For other users, install 3.9 from [pyenv](https://github.com/yyuu/pyenv)

Running requires:

1. Android 5.0 (Lollipop, API 21) or above
2. arm, arm64, x86 or x86-64

Build
-----

1. Run `./clean.sh` for good measure.
2. For every API Level/architecture combination you wish to build for:
   * `ARCH=arm ANDROID_API=21 ./build.sh` to build everything!

Build using Docker
------------------

```
docker build -t python3-android-base docker
docker run --rm -it --user $(id -u):$(id -g) -v $(pwd):/python3-android --env ARCH=arm --env ANDROID_API=21 python3-android-base
```

Installation
------------

1. Make sure `adb shell` works fine
2. Copy all files in `build` to a folder on the device (e.g., ```/data/local/tmp/python3```). Note that on most devices `/sdcard` is not on a POSIX-compliant filesystem, so the python binary will not run from there.
3. In adb shell:
<pre>
cd /data/local/tmp/build
. ./env.sh
python3
</pre>
   And have fun!

SSL/TLS
-------
SSL certificates have old and new naming schemes. Android uses the old scheme yet the latest OpenSSL uses the new one. If you got ```CERTIFICATE_VERIFY_FAILED``` when using SSL/TLS in Python, you need to collect system certificates:
```
cd /data/local/tmp/build
mkdir -p etc/ssl
cat /system/etc/security/cacerts/* > etc/ssl/cert.pem
```
Path for certificates may vary with device vendor and/or Android version. Note that this approach only collects system certificates. If you need to collect user-installed certificates, most likely root access on your Android device is needed.

Check SSL/TLS functionality with:
```
import urllib.request
print(urllib.request.urlopen('https://httpbin.org/ip').read().decode('ascii'))
```


Known Issues
------------

No big issues! yay
