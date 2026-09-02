Name:           hyprpaper
Version:        0.8.4
Release:        2%{?dist}
Summary:        Wayland wallpaper utility for Hyprland
License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprpaper
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz

ExcludeArch:    %{ix86}
BuildRequires:  cmake
BuildRequires:  file-devel
BuildRequires:  gcc-c++
BuildRequires:  hyprwayland-scanner-devel >= 0.4.0
BuildRequires:  pkgconfig(hyprlang) >= 0.6.0
BuildRequires:  pkgconfig(hyprtoolkit) >= 0.4.1
BuildRequires:  pkgconfig(hyprutils)
BuildRequires:  pkgconfig(hyprwire)
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(pixman-1)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-protocols)
BuildRequires:  systemd-rpm-macros

%description
Hyprpaper is a fast wallpaper utility with per-output support.

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
%{_bindir}/hyprpaper
%{_userunitdir}/hyprpaper.service

%changelog
* Tue Sep 01 2026 COPR Maintainer <noreply@example.invalid> - 0.8.4-2
- Add the Wayland protocols needed by the source scanner

* Tue Sep 01 2026 COPR Maintainer <noreply@example.invalid> - 0.8.4-1
- Initial package
