Name:           hyprtoolkit
Version:        0.5.4
Release:        2%{?dist}
Summary:        Hyprland graphical user interface toolkit
License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprtoolkit
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz

ExcludeArch:    %{ix86}
BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  hyprwayland-scanner-devel >= 0.4.0
BuildRequires:  pkgconfig(aquamarine) >= 0.10.0
BuildRequires:  pkgconfig(cairo)
BuildRequires:  pkgconfig(egl)
BuildRequires:  pkgconfig(gbm)
BuildRequires:  pkgconfig(hyprgraphics) >= 0.3.0
BuildRequires:  pkgconfig(hyprlang) >= 0.6.0
BuildRequires:  pkgconfig(hyprutils) >= 0.11.0
BuildRequires:  pkgconfig(iniparser)
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(pango)
BuildRequires:  pkgconfig(pangocairo)
BuildRequires:  pkgconfig(pixman-1)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-protocols)
BuildRequires:  pkgconfig(xkbcommon)

%description
First-party GUI toolkit shared by Hyprland applications.

%package devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       pkgconfig(aquamarine) >= 0.10.0
Requires:       pkgconfig(hyprgraphics) >= 0.3.0
Requires:       pkgconfig(hyprutils) >= 0.11.0

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
%{_libdir}/libhyprtoolkit.so.*

%files devel
%{_includedir}/hyprtoolkit/
%{_libdir}/libhyprtoolkit.so
%{_libdir}/pkgconfig/hyprtoolkit.pc

%changelog
* Tue Sep 01 2026 COPR Maintainer <noreply@example.invalid> - 0.5.4-2
- Add development dependencies exposed by public headers

* Tue Sep 01 2026 COPR Maintainer <noreply@example.invalid> - 0.5.4-1
- Initial package
