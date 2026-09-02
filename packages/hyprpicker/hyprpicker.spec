Name:           hyprpicker
Version:        0.4.7
Release:        1%{?dist}
Summary:        Wayland color picker for Hyprland
License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprpicker
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz

ExcludeArch:    %{ix86}
BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  hyprwayland-scanner-devel >= 0.4.0
BuildRequires:  pkgconfig(cairo)
BuildRequires:  pkgconfig(hyprutils)
BuildRequires:  pkgconfig(libjpeg)
BuildRequires:  pkgconfig(pango)
BuildRequires:  pkgconfig(pangocairo)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-protocols)
BuildRequires:  pkgconfig(xkbcommon)

%description
Hyprpicker is a wlroots-compatible Wayland color picker.

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
%{_bindir}/hyprpicker
%{_mandir}/man1/hyprpicker.1*

%changelog
* Tue Sep 01 2026 COPR Maintainer <noreply@example.invalid> - 0.4.7-1
- Initial package
