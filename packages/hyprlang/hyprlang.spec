Name:           hyprlang
Version:        0.6.8
Release:        1%{?dist}
Summary:        Hypr configuration language library
License:        LGPL-3.0-only
URL:            https://github.com/hyprwm/hyprlang
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz

ExcludeArch:    %{ix86}
BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  pkgconfig(hyprutils) >= 0.7.1

%description
The official parser and implementation library for Hypr configuration files.

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

%check
%ctest

%files
%license LICENSE
%doc README.md
%{_libdir}/libhyprlang.so.*

%files devel
%{_includedir}/hyprlang.hpp
%{_libdir}/libhyprlang.so
%{_libdir}/pkgconfig/hyprlang.pc

%changelog
* Tue Sep 01 2026 COPR Maintainer <noreply@example.invalid> - 0.6.8-1
- Initial package
