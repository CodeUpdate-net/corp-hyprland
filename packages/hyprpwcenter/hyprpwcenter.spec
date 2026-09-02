Name:           hyprpwcenter
Version:        0.1.2
Release:        1%{?dist}
Summary:        PipeWire control center for Hyprland
License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprpwcenter
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz

ExcludeArch:    %{ix86}
BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  pkgconfig(hyprtoolkit)
BuildRequires:  pkgconfig(hyprutils) >= 0.10.2
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(libpipewire-0.3)
BuildRequires:  pkgconfig(pixman-1)

%description
Hyprpwcenter is a graphical PipeWire volume and device control center.

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
%{_bindir}/hyprpwcenter
%{_datadir}/applications/hyprpwcenter.desktop

%changelog
* Tue Sep 01 2026 COPR Maintainer <noreply@example.invalid> - 0.1.2-1
- Initial package
