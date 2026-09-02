Name:           hypridle
Version:        0.1.8
Release:        1%{?dist}
Summary:        Hyprland idle management daemon
License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hypridle
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz

ExcludeArch:    %{ix86}
BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  hyprwayland-scanner-devel >= 0.4.4
BuildRequires:  pkgconfig(hyprland-protocols) >= 0.6.0
BuildRequires:  pkgconfig(hyprlang) >= 0.6.0
BuildRequires:  pkgconfig(hyprutils)
BuildRequires:  pkgconfig(sdbus-c++)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-protocols)
BuildRequires:  systemd-rpm-macros

%description
Hypridle is Hyprland's configurable idle management daemon.

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
%{_bindir}/hypridle
%{_datadir}/hypr/hypridle.conf
%{_userunitdir}/hypridle.service

%changelog
* Tue Sep 01 2026 COPR Maintainer <noreply@example.invalid> - 0.1.8-1
- Initial package
