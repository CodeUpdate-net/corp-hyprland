Name:           hyprutils
Version:        0.14.1
Release:        2%{?dist}
Summary:        Hyprland utility library
License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprutils
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz

ExcludeArch:    %{ix86}
BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  pkgconfig(pixman-1)

%description
Shared utility functionality used across the Hyprland ecosystem.

%package devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       pkgconfig(pixman-1)

%description devel
Headers and pkg-config metadata for developing against %{name}.

%prep
%autosetup -p1

%build
%cmake -DCMAKE_BUILD_TYPE=Release
%cmake_build

%install
%cmake_install
sed -i '/^Version:/a Requires: pixman-1' \
  %{buildroot}%{_libdir}/pkgconfig/hyprutils.pc

%files
%license LICENSE
%doc README.md
%{_libdir}/libhyprutils.so.*

%files devel
%{_includedir}/hyprutils/
%{_libdir}/libhyprutils.so
%{_libdir}/pkgconfig/hyprutils.pc

%changelog
* Tue Sep 01 2026 COPR Maintainer <noreply@example.invalid> - 0.14.1-2
- Add development dependency exposed by public headers

* Tue Sep 01 2026 COPR Maintainer <noreply@example.invalid> - 0.14.1-1
- Initial package
