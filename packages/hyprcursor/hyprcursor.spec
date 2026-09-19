Name:           hyprcursor
Version:        0.1.13
Release:        3%{?dist}
Summary:        Hyprland cursor format library and utilities
License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprcursor
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source1:        test-extraction.py
Patch0:         0001-quote-xcur2png-input-path.patch
Patch1:         0002-private-extraction-directory.patch

ExcludeArch:    %{ix86}
BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  python3
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
Requires:       pkgconfig(cairo)

%description devel
Headers and pkg-config metadata for developing against %{name}.

%prep
%autosetup -p1

%build
%cmake -DCMAKE_BUILD_TYPE=Release
%cmake_build

%install
%cmake_install
sed -i '/^Version:/a Requires: cairo' \
  %{buildroot}%{_libdir}/pkgconfig/hyprcursor.pc

%check
python3 %{SOURCE1} %{_vpath_builddir}/hyprcursor-util

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
* Fri Sep 18 2026 COPR Maintainer <noreply@example.invalid> - 0.1.13-3
- Use private temporary directories for cursor extraction, with automatic cleanup

* Tue Sep 01 2026 COPR Maintainer <noreply@example.invalid> - 0.1.13-2
- Add development dependency exposed by public headers

* Tue Sep 01 2026 COPR Maintainer <noreply@example.invalid> - 0.1.13-1
- Initial package with safe shell quoting for XCursor paths
