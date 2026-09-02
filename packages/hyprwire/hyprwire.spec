Name:           hyprwire
Version:        0.3.1
Release:        2%{?dist}
Summary:        Hyprland IPC wire protocol library
License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprwire
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz

ExcludeArch:    %{ix86}
BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  cmake(pugixml)
BuildRequires:  pkgconfig(hyprutils) >= 0.9.0
BuildRequires:  pkgconfig(libffi)

%description
Fast and consistent wire protocol and scanner for Hyprland IPC.

%package devel
Summary:        Development files and scanner for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       pkgconfig(hyprutils) >= 0.9.0

%description devel
Headers, scanner, and build metadata for developing against %{name}.

%prep
%autosetup -p1

%build
%cmake -DCMAKE_BUILD_TYPE=Release
%cmake_build

%install
%cmake_install
sed -i '/^Version:/a Requires: hyprutils >= 0.9.0' \
  %{buildroot}%{_libdir}/pkgconfig/hyprwire.pc

%files
%license LICENSE
%doc README.md
%{_libdir}/libhyprwire.so.*

%files devel
%{_bindir}/hyprwire-scanner
%{_includedir}/hyprwire/
%{_libdir}/libhyprwire.so
%{_libdir}/pkgconfig/hyprwire.pc
%{_libdir}/pkgconfig/hyprwire-scanner.pc
%{_libdir}/cmake/hyprwire-scanner/

%changelog
* Tue Sep 01 2026 COPR Maintainer <noreply@example.invalid> - 0.3.1-2
- Add development dependency exposed by public headers

* Tue Sep 01 2026 COPR Maintainer <noreply@example.invalid> - 0.3.1-1
- Initial package
