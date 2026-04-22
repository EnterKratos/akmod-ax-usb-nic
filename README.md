# akmod-ax-usb-nic

Fedora akmod package for the ASIX AX88179/AX88178A USB Gigabit Ethernet vendor driver.

## Why this exists

The in-kernel `ax88179_178a` driver causes a register/unregister crash loop on
some AX88179-based adapters such as the BIONIK BNK-9018. The vendor driver from
ASIX does not exhibit this problem.

## Source and modifications

The driver source is the **official ASIX Linux driver v4.0.0**, downloaded from:
https://www.asix.com.tw/en/support/download/file/2116

The only modification to the official source is in `ax88179-makefile.patch`:
a single character change to `Makefile` that allows the kernel build directory
to be overridden at compile time (`KDIR := ...` → `KDIR ?= ...`). This is
required for akmod out-of-tree builds and has no effect on normal usage.

The blacklist config (`ax_usb_nic_blacklist.conf`) is shipped unmodified from
the official ASIX source. It blacklists the in-kernel `ax88179_178a` driver to
prevent it from claiming the device before `ax_usb_nic` can load.

## Installation

```bash
dnf copr enable enterkratos/akmod-ax-usb-nic
rpm-ostree install akmod-ax-usb-nic   # Fedora Kinoite / Silverblue
# or
sudo dnf install akmod-ax-usb-nic     # standard Fedora
```

The COPR project page is at:
https://copr.fedorainfracloud.org/coprs/enterkratos/akmod-ax-usb-nic/

The source for this package is at:
https://github.com/EnterKratos/akmod-ax-usb-nic

## Updating to a new upstream version

ASIX publish updated drivers at:
https://www.asix.com.tw/en/support/download

When a new version is released (replace `X.X.X` throughout the following steps and in `ax-usb-nic-kmod.spec` with the actual version number):

1. Download the new tarball and note the direct download URL.

2. Verify and record the SHA256:
   ```bash
   sha256sum ASIX_USB_NIC_Linux_Driver_Source_vX.X.X.tar.bz2
   ```
   Update this value in the `%prep` section of `ax-usb-nic-kmod.spec`.

3. Check the patch still applies cleanly:
   ```bash
   tar -xjf ASIX_USB_NIC_Linux_Driver_Source_vX.X.X.tar.bz2
   cd ASIX_USB_NIC_Linux_Driver_Source_vX.X.X
   patch -p0 --dry-run < /path/to/akmod-ax-usb-nic/ax88179-makefile.patch
   cd ..
   rm -rf ASIX_USB_NIC_Linux_Driver_Source_vX.X.X
   ```
   If the dry run fails, the Makefile changed upstream — see
   [Regenerating the patch](#regenerating-the-patch) below.

### Regenerating the patch

If the upstream Makefile changes and the existing patch no longer applies, generate
a new one as follows:

```bash
tar -xjf ASIX_USB_NIC_Linux_Driver_Source_vX.X.X.tar.bz2
cd ASIX_USB_NIC_Linux_Driver_Source_vX.X.X
cp Makefile Makefile.orig
sed -i 's/KDIR\t:= /KDIR\t?= /' Makefile
diff -u Makefile.orig Makefile > ../ax88179-makefile.patch
cd ..
rm -rf ASIX_USB_NIC_Linux_Driver_Source_vX.X.X
```

The change being made is `KDIR := ...` → `KDIR ?= ...` (`:=` to `?=`). This allows
the kernel build directory to be overridden at compile time, which is required for
akmod out-of-tree builds. Verify the resulting patch looks correct before committing:

```bash
cat ax88179-makefile.patch
```

4. Update `ax-usb-nic-kmod.spec`:
   - `%global driver_version` — new version number
   - `%global driver_sha256` — new SHA256
   - `%changelog` — new entry at the top, in this format:
     ```
     * Day Mon DD YYYY EnterKratos <15807441+EnterKratos@users.noreply.github.com> - X.X.X-1
     - Update to upstream ASIX vendor driver vX.X.X
     ```

5. Commit and push. The GitHub webhook will automatically trigger a COPR rebuild.
