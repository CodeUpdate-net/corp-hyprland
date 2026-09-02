Name:           hyprcursor
Version:        0.1.13
Release:        1%{?dist}
Summary:        Hyprland cursor format library and utilities
License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprcursor
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
Patch0:         0001-quote-xcur2png-input-path.patch

ExcludeArch:    %{ix86}
BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  pkgconfig(cairo)
BuildRequires:  pkgconfig(hyprlang) >= 0.4.2
BuildRequires:  pkgconfig(librsvg-2.0)
BuildRequires:  pkgconfig(libzip)
BuildRequires:  pkgconfig(tomlplusplus)

%description
Library and conversion utility for the Hyprland cursor format.

%package devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
Headers and pkg-config metadata for developing against %{name}.

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
%{_bindir}/hyprcursor-util
%{_libdir}/libhyprcursor.so.*

%files devel
%{_includedir}/hyprcursor.hpp
%{_includedir}/hyprcursor/
%{_libdir}/libhyprcursor.so
%{_libdir}/pkgconfig/hyprcursor.pc

%changelog
* Tue Sep 01 2026 COPR Maintainer <noreply@example.invalid> - 0.1.13-1
- Initial package with safe shell quoting for XCursor paths
