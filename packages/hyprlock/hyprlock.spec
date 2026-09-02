Name:           hyprlock
Version:        0.9.6
Release:        1%{?dist}
Summary:        Screen locker for Hyprland
License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprlock
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz

ExcludeArch:    %{ix86}
BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  hyprwayland-scanner-devel >= 0.4.4
BuildRequires:  pkgconfig(cairo)
BuildRequires:  pkgconfig(egl)
BuildRequires:  pkgconfig(gbm)
BuildRequires:  pkgconfig(hyprgraphics) >= 0.1.6
BuildRequires:  pkgconfig(hyprlang) >= 0.6.0
BuildRequires:  pkgconfig(hyprutils) >= 0.11.0
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(pam)
BuildRequires:  pkgconfig(pangocairo)
BuildRequires:  pkgconfig(sdbus-c++) >= 2.0.0
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-egl)
BuildRequires:  pkgconfig(wayland-protocols) >= 1.35
BuildRequires:  pkgconfig(xkbcommon)

%description
Hyprlock is a GPU-accelerated screen locker for the Hyprland ecosystem.

%prep
%autosetup -p1

%build
%cmake -DCMAKE_BUILD_TYPE=Release
%cmake_build

%install
%cmake_install

%files
%license LICENSE
%doc README.md
%config(noreplace) %{_sysconfdir}/pam.d/hyprlock
%{_bindir}/hyprlock
%{_datadir}/hypr/hyprlock.conf

%changelog
* Tue Sep 01 2026 COPR Maintainer <noreply@example.invalid> - 0.9.6-1
- Initial package
