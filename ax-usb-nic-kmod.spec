# Determine build mode: local 'current' kernel or 'akmod' for akmods service
%if 0%{!?buildforkernels:1}
%global buildforkernels akmod
%endif

%global debug_package %{nil}

# Update both of these when bumping to a new upstream release.
# Source0 URL may also need updating — check:
# https://www.asix.com.tw/en/support/download
%global driver_version 4.0.0
%global driver_sha256  9a08945f4d285c1751747edffc13d82b62044e9b3bc7d09831038207f348442f

Name:           ax-usb-nic-kmod
Version:        %{driver_version}
Release:        1%{?dist}
Summary:        Vendor kernel module for ASIX AX88179/AX88178A USB Gigabit Ethernet

# License is GPL-2.0-or-later per the license text in all source files.
# SPDX-License-Identifier tags in the source incorrectly say GPL-2.0.
License:        GPL-2.0-or-later
URL:            https://www.asix.com.tw/en/product/USBEthernet

# Official ASIX source. URL may change between versions.
# SHA256 is verified in %%prep — update %%{driver_sha256} above when bumping.
Source0:        https://www.asix.com.tw/en/support/download/file/2116#/ASIX_USB_NIC_Linux_Driver_Source_v%{driver_version}.tar.bz2

# Allows KDIR to be overridden at build time so the module can be compiled
# against a kernel other than the currently running one. Changes KDIR from
# := (immediate assignment) to ?= (default, overridable). This is the only
# modification made to the official ASIX source.
# Not submitted upstream — ASIX do not maintain a public git repository.
Patch0:         ax88179-makefile.patch

# Only x86_64 has been tested. The driver source is likely portable but
# has not been verified on other architectures.
ExclusiveArch:  x86_64

# kmodtool build requirements
%global AkmodsBuildRequires %{_bindir}/kmodtool
BuildRequires:  %{AkmodsBuildRequires}
%{!?kernels:BuildRequires: gcc}
%{!?kernels:BuildRequires: make}
%{!?kernels:BuildRequires: elfutils-libelf-devel}
%{!?kernels:BuildRequires: buildsys-build-rpmfusion-kerneldevpkgs-%{?buildforkernels:%{buildforkernels}}%{!?buildforkernels:current}-%{_target_cpu}}

# kmodtool generates subpackage definitions
%{expand:%(kmodtool --target %{_target_cpu} --repo rpmfusion --kmodname ax-usb-nic %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null)}


%description
Vendor driver for ASIX AX88179 and AX88178A USB 3.0/2.0 Gigabit Ethernet
adapters. Replaces the in-kernel ax88179_178a driver, which causes a
register/unregister crash loop on some systems (including Nintendo Switch
USB ethernet adapters such as the BIONIK BNK-9018).

Source is the official ASIX Linux driver. The only modification is a
one-character change to the Makefile (see ax88179-makefile.patch) to allow
the kernel build directory to be overridden, which is required for akmod
out-of-tree builds.


%prep
# Verify the source tarball matches the expected SHA256
echo "%{driver_sha256}  %{SOURCE0}" | sha256sum --check

# Verify kmodtool is working
%{?kmodtool_check}
kmodtool --target %{_target_cpu} --repo rpmfusion --kmodname ax-usb-nic %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null

%setup -q -n ASIX_USB_NIC_Linux_Driver_Source_v%{driver_version}
%patch 0 -p0

# Set up build directories for each kernel version
for kernel_version in %{?kernel_versions}; do
    cp -a . _kmod_build_${kernel_version%%___*}
done


%build
for kernel_version in %{?kernel_versions}; do
    make -C ${kernel_version##*___} \
        M=${PWD}/_kmod_build_${kernel_version%%___*} \
        KDIR=${kernel_version##*___} \
        modules
done


%install
for kernel_version in %{?kernel_versions}; do
    install -Dm755 \
        _kmod_build_${kernel_version%%___*}/ax_usb_nic.ko \
        %{buildroot}%{kmodinstdir_prefix}${kernel_version%%___*}%{kmodinstdir_postfix}/ax_usb_nic.ko
done
%{?akmod_install}

# Install blacklist — shipped with the official ASIX source
install -Dm644 ax_usb_nic_blacklist.conf \
    %{buildroot}%{_prefix}/lib/modprobe.d/ax_usb_nic_blacklist.conf

# Install upstream documentation
install -Dm644 Readme %{buildroot}%{_docdir}/%{name}/Readme





%check
# No tests — kernel modules cannot be meaningfully tested at build time
# without a running kernel matching the build target.


%changelog
* Wed Apr 22 2026 EnterKratos <15807441+EnterKratos@users.noreply.github.com> - 4.0.0-1
- Initial package using official ASIX vendor driver v4.0.0
- Single Makefile patch for out-of-tree akmod builds (ax88179-makefile.patch)
- Blacklists in-kernel ax88179_178a to prevent crash loop on AX88179 devices
