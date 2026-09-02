Name:           hyprsunset
Version:        0.4.0
Release:        1%{?dist}
Summary:        Blue-light filter for Hyprland
License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprsunset
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz

ExcludeArch:    %{ix86}
BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  hyprwayland-scanner-devel >= 0.4.0
BuildRequires:  pkgconfig(hyprland-protocols) >= 0.4.0
BuildRequires:  pkgconfig(hyprlang)
BuildRequires:  pkgconfig(hyprutils)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-protocols)
BuildRequires:  systemd-rpm-macros

%description
Hyprsunset adjusts display color temperature using Hyprland protocols.

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
%{_bindir}/hyprsunset
%{_userunitdir}/hyprsunset.service

%changelog
* Tue Sep 01 2026 COPR Maintainer <noreply@example.invalid> - 0.4.0-1
- Initial package
