Name:           aquamarine
Version:        0.15.0
Release:        1%{?dist}
Summary:        Lightweight Linux rendering backend library
License:        BSD-3-Clause
URL:            https://github.com/hyprwm/aquamarine
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz

ExcludeArch:    %{ix86}
BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  hyprwayland-scanner-devel >= 0.4.0
BuildRequires:  pkgconfig(hwdata)
BuildRequires:  pkgconfig(egl)
BuildRequires:  pkgconfig(gbm)
BuildRequires:  pkgconfig(hyprutils) >= 0.8.0
BuildRequires:  pkgconfig(libdisplay-info)
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(libinput) >= 1.26.0
BuildRequires:  pkgconfig(libseat) >= 0.8.0
BuildRequires:  pkgconfig(libudev)
BuildRequires:  pkgconfig(pixman-1)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-protocols)

%description
Aquamarine is the display and rendering backend library used by Hyprland.

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
%{_libdir}/libaquamarine.so.*

%files devel
%{_includedir}/aquamarine/
%{_libdir}/libaquamarine.so
%{_libdir}/pkgconfig/aquamarine.pc

%changelog
* Tue Sep 01 2026 COPR Maintainer <noreply@example.invalid> - 0.15.0-1
- Initial package
