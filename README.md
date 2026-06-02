# akmod-ax-usb-nic

Fedora akmod package for the ASIX AX88179/AX88178A USB Gigabit Ethernet vendor driver.

## Why this exists

The in-kernel `ax88179_178a` driver causes a register/unregister crash loop on
some AX88179-based adapters such as the BIONIK BNK-9018. The vendor driver from
ASIX does not exhibit this problem.

## Source and modifications

The driver source is the official ASIX Linux vendor tarball. The current
version, download URL, and SHA256 are recorded in `ax-usb-nic-kmod.spec` and
verified at build time in `%prep`.

Packaging changes to the upstream source:

- `ax88179-makefile.patch` — a single character change to `Makefile` that
  allows the kernel build directory to be overridden at compile time
  (`KDIR := ...` → `KDIR ?= ...`). Required for akmod out-of-tree builds.
- `%prep` — upstream `Makefile` line endings are normalized to LF before
  patching (`sed -i 's/\r$//' Makefile`). Recent ASIX tarballs ship CRLF
  line endings; the patch is kept LF-only in git.

The blacklist config (`ax_usb_nic_blacklist.conf`) is shipped unmodified from
the official ASIX source. It blacklists the in-kernel `ax88179_178a` driver to
prevent it from claiming the device before `ax_usb_nic` can load.

## Installation

Supported Fedora releases are listed on the COPR project page:
https://copr.fedorainfracloud.org/coprs/enterkratos/akmod-ax-usb-nic/

**Fedora Kinoite / Silverblue** — first install:
```bash
sudo wget -O /etc/yum.repos.d/enterkratos-akmod-ax-usb-nic.repo \
    https://copr.fedorainfracloud.org/coprs/enterkratos/akmod-ax-usb-nic/repo/fedora-$(rpm -E %fedora)/enterkratos-akmod-ax-usb-nic-fedora-$(rpm -E %fedora).repo
rpm-ostree install akmod-ax-usb-nic
systemctl reboot
```

**Fedora Kinoite / Silverblue** — upgrade to a new COPR release:
```bash
rpm-ostree refresh-md
rpm-ostree upgrade
systemctl reboot
```

If the layered package does not bump to the new version after upgrade:
```bash
rpm-ostree uninstall akmod-ax-usb-nic
rpm-ostree install akmod-ax-usb-nic
systemctl reboot
```

**Standard Fedora**:
```bash
sudo dnf copr enable enterkratos/akmod-ax-usb-nic
sudo dnf install akmod-ax-usb-nic
```

To upgrade: `sudo dnf upgrade akmod-ax-usb-nic`, then `sudo akmods --force`
and reboot.

## Maintenance

Releases are triggered by pushing a Git tag in the format `PKGNAME-VERSION-RELEASE`.
COPR picks up the tag and triggers a build automatically. For example:

```bash
git tag ax-usb-nic-kmod-X.X.X-X
git push origin master ax-usb-nic-kmod-X.X.X-X
```

The `Release` field resets to `1` when the upstream driver version changes, and
increments for packaging-only fixes (e.g. `4.0.0-2`).

Each release requires a `%changelog` entry in `ax-usb-nic-kmod.spec`. See the
Fedora packaging guidelines for the required format:
https://docs.fedoraproject.org/en-US/packaging-guidelines/#changelogs

### Updating to a new upstream driver version

ASIX publish updated drivers at:
https://www.asix.com.tw/en/support/download

When a new version is released (replace `X.X.X` with the actual version number):

1. Download the new tarball and note the direct download URL.

2. Verify the SHA256:
   ```bash
   sha256sum ASIX_USB_NIC_Linux_Driver_Source_vX.X.X.tar.bz2
   ```

3. Check the patch still applies cleanly (normalize CRLF first, as in `%prep`):
   ```bash
   tar -xjf ASIX_USB_NIC_Linux_Driver_Source_vX.X.X.tar.bz2
   cd ASIX_USB_NIC_Linux_Driver_Source_vX.X.X
   sed -i 's/\r$//' Makefile
   patch -p0 --dry-run < /path/to/akmod-ax-usb-nic/ax88179-makefile.patch
   cd ..
   rm -rf ASIX_USB_NIC_Linux_Driver_Source_vX.X.X
   ```
   If the dry run fails see [Regenerating the patch](#regenerating-the-patch) below.

4. Update `ax-usb-nic-kmod.spec`:
   - `%global driver_version` — new version number
   - `%global driver_sha256` — new SHA256
   - `Source0` URL if the download link changed
   - `Release` — reset to `1`
   - `%changelog` — new entry at the top

5. Commit, tag, and push:
   ```bash
   git add ax-usb-nic-kmod.spec ax88179-makefile.patch  # include patch if regenerated
   git commit -m "Update to upstream ASIX driver vX.X.X"
   git tag ax-usb-nic-kmod-X.X.X-1
   git push origin master ax-usb-nic-kmod-X.X.X-1
   ```

### Regenerating the patch

If the upstream Makefile changes and the existing patch no longer applies:

```bash
tar -xjf ASIX_USB_NIC_Linux_Driver_Source_vX.X.X.tar.bz2
cd ASIX_USB_NIC_Linux_Driver_Source_vX.X.X
sed -i 's/\r$//' Makefile
cp Makefile Makefile.orig
sed -i 's/KDIR\t:= /KDIR\t?= /' Makefile
diff -u Makefile.orig Makefile > ../ax88179-makefile.patch
cd ..
rm -rf ASIX_USB_NIC_Linux_Driver_Source_vX.X.X
```

The change being made is `KDIR := ...` → `KDIR ?= ...` (`:=` to `?=`). Verify
the patch looks correct before committing:

```bash
cat ax88179-makefile.patch
```

### Packaging fix (no upstream change)

1. Bump `Release` in `ax-usb-nic-kmod.spec` (e.g. `1` → `2`)
2. Add a `%changelog` entry describing the fix
3. Commit, tag, and push:
   ```bash
   git add ax-usb-nic-kmod.spec
   git commit -m "Description of the fix"
   git tag ax-usb-nic-kmod-4.0.0-2
   git push origin master ax-usb-nic-kmod-4.0.0-2
   ```
