Name:           hyprland-plugins
Version:        0.56.0
Release:        1%{?dist}
Summary:        Official plugins for Hyprland
License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprland-plugins
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz

ExcludeArch:    %{ix86}
BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  hyprland-devel >= 0.56.0
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(libinput)
BuildRequires:  pkgconfig(libudev)
BuildRequires:  pkgconfig(pangocairo)
BuildRequires:  pkgconfig(pixman-1)
BuildRequires:  pkgconfig(wayland-server)
BuildRequires:  pkgconfig(xkbcommon)
Requires:       hyprland%{?_isa} >= 0.56.0

%description
Official borders, window-bar, focus, and compatibility plugins for Hyprland.

%prep
%autosetup -p1

%build
%cmake \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_LIBDIR=%{_lib}
%cmake_build

%install
%cmake_install

%files
%license LICENSE
%doc README.md
%{_libdir}/libborders-plus-plus.so
%{_libdir}/libcsgo-vulkan-fix.so
%{_libdir}/libhyprbars.so
%{_libdir}/libhyprfocus.so

%changelog
* Tue Sep 01 2026 COPR Maintainer <noreply@example.invalid> - 0.56.0-1
- Initial package
