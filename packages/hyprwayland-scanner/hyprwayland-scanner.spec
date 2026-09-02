Name:           hyprwayland-scanner
Version:        0.4.6
Release:        1%{?dist}
Summary:        Hyprland implementation of wayland-scanner for C++
License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprwayland-scanner
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz

ExcludeArch:    %{ix86}
BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  cmake(pugixml)

%description
Hyprland's Wayland protocol scanner and C++ code generator.

%package devel
Summary:        Protocol scanner and development metadata

%description devel
The Hyprland Wayland scanner executable, pkg-config file, and CMake metadata.

%prep
%autosetup -p1

%build
%cmake -DCMAKE_BUILD_TYPE=Release
%cmake_build

%install
%cmake_install

%files devel
%license LICENSE
%doc README.md
%{_bindir}/hyprwayland-scanner
%{_libdir}/pkgconfig/hyprwayland-scanner.pc
%{_libdir}/cmake/hyprwayland-scanner/

%changelog
* Tue Sep 01 2026 COPR Maintainer <noreply@example.invalid> - 0.4.6-1
- Initial package
