Name:           hyprgraphics
Version:        0.5.1
Release:        2%{?dist}
Summary:        Graphics library for the Hyprland ecosystem
License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprgraphics
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz

ExcludeArch:    %{ix86}
BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  pkgconfig(cairo)
BuildRequires:  pkgconfig(glesv2)
BuildRequires:  pkgconfig(hyprutils)
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(libheif)
BuildRequires:  pkgconfig(libjpeg)
BuildRequires:  pkgconfig(libjxl)
BuildRequires:  pkgconfig(libjxl_cms)
BuildRequires:  pkgconfig(libjxl_threads)
BuildRequires:  pkgconfig(libmagic)
BuildRequires:  pkgconfig(libpng)
BuildRequires:  pkgconfig(librsvg-2.0)
BuildRequires:  pkgconfig(libwebp)
BuildRequires:  pkgconfig(pangocairo)
BuildRequires:  pkgconfig(pixman-1)

%description
Graphics and resource utilities shared by Hyprland projects.

%package devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       pkgconfig(cairo)
Requires:       pkgconfig(glesv2)
Requires:       pkgconfig(hyprutils)

%description devel
Headers and pkg-config metadata for developing against %{name}.

%prep
%autosetup -p1

%build
%cmake -DCMAKE_BUILD_TYPE=Release
%cmake_build

%install
%cmake_install
sed -i '/^Version:/a Requires: cairo, glesv2, hyprutils' \
  %{buildroot}%{_libdir}/pkgconfig/hyprgraphics.pc

%check
%ctest

%files
%license LICENSE
%doc README.md
%{_libdir}/libhyprgraphics.so.*

%files devel
%{_includedir}/hyprgraphics/
%{_libdir}/libhyprgraphics.so
%{_libdir}/pkgconfig/hyprgraphics.pc

%changelog
* Tue Sep 01 2026 COPR Maintainer <noreply@example.invalid> - 0.5.1-2
- Add development dependencies exposed by public headers

* Tue Sep 01 2026 COPR Maintainer <noreply@example.invalid> - 0.5.1-1
- Initial package
