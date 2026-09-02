Name:           hyprland
Version:        0.56.2
Release:        3%{?dist}
Summary:        Dynamic tiling Wayland compositor
License:        BSD-3-Clause
URL:            https://github.com/hyprwm/Hyprland
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz

ExcludeArch:    %{ix86}
BuildRequires:  bash
BuildRequires:  cmake >= 3.30
BuildRequires:  gcc-c++
BuildRequires:  glslang-devel
BuildRequires:  pkgconfig(aquamarine) >= 0.9.3
BuildRequires:  pkgconfig(cairo)
BuildRequires:  pkgconfig(egl)
BuildRequires:  pkgconfig(gbm)
BuildRequires:  pkgconfig(gio-2.0)
BuildRequires:  glaze-devel >= 7.0
BuildRequires:  pkgconfig(hyprcursor) >= 0.1.7
BuildRequires:  pkgconfig(hyprgraphics) >= 0.5.1
BuildRequires:  pkgconfig(hyprland-protocols) >= 0.7.0
BuildRequires:  pkgconfig(hyprlang) >= 0.6.7
BuildRequires:  pkgconfig(hyprutils) >= 0.14.0
BuildRequires:  pkgconfig(hyprwire)
BuildRequires:  pkgconfig(lcms2)
BuildRequires:  pkgconfig(libeis-1.0)
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(libinput) >= 1.29
%if 0%{?fedora} < 45
BuildRequires:  pkgconfig(lua55) >= 5.5
%else
BuildRequires:  pkgconfig(lua) >= 5.5
%endif
BuildRequires:  pkgconfig(muparser)
BuildRequires:  pkgconfig(pango)
BuildRequires:  pkgconfig(pangocairo)
BuildRequires:  pkgconfig(pixman-1)
BuildRequires:  pkgconfig(readline)
BuildRequires:  pkgconfig(re2)
BuildRequires:  pkgconfig(tomlplusplus)
BuildRequires:  udis86-devel >= 1.7.2
BuildRequires:  pkgconfig(uuid)
BuildRequires:  pkgconfig(wayland-protocols) >= 1.49
BuildRequires:  pkgconfig(wayland-scanner)
BuildRequires:  pkgconfig(wayland-server) >= 1.22.91
BuildRequires:  pkgconfig(xcb)
BuildRequires:  pkgconfig(xcb-composite)
BuildRequires:  pkgconfig(xcb-errors)
BuildRequires:  pkgconfig(xcb-icccm)
BuildRequires:  pkgconfig(xcb-render)
BuildRequires:  pkgconfig(xcb-res)
BuildRequires:  pkgconfig(xcb-xfixes)
BuildRequires:  pkgconfig(xcursor)
BuildRequires:  pkgconfig(xkbcommon) >= 1.11
BuildRequires:  hyprwayland-scanner-devel >= 0.3.10
BuildRequires:  systemd-rpm-macros
Requires:       xorg-x11-server-Xwayland
Recommends:     uwsm >= 0.26.7
Recommends:     xdg-desktop-portal-hyprland

%description
Hyprland is a dynamic tiling Wayland compositor with modern animations and
extensive configuration support.

%package devel
Summary:        Development files for Hyprland plugins
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       glslang-devel
Requires:       pkgconfig(libeis-1.0)

%description devel
Headers and pkg-config metadata for building Hyprland plugins.

%prep
%autosetup -p1 -n Hyprland-%{version}

%build
export GIT_COMMIT_HASH=efb50993780079460b0cbed1363e2166a2de1d9f
export GIT_TAG=v%{version}
%cmake \
  -DCMAKE_BUILD_TYPE=Release \
  -DFETCHCONTENT_FULLY_DISCONNECTED=ON \
  -DNO_UWSM=OFF \
  -DUSE_TRACY=OFF \
  -DWITH_TESTS=OFF
%cmake_build

%install
%cmake_install
%if 0%{?fedora} < 45
sed -i '/^Requires:/ s/$/, libeis-1.0, lua55 >= 5.5/' \
  %{buildroot}%{_datadir}/pkgconfig/hyprland.pc
%else
sed -i '/^Requires:/ s/$/, libeis-1.0, lua >= 5.5/' \
  %{buildroot}%{_datadir}/pkgconfig/hyprland.pc
%endif

%files
%license LICENSE
%doc README.md
%{_bindir}/Hyprland
%{_bindir}/hyprland
%{_bindir}/hyprctl
%{_bindir}/hyprpm
%{_bindir}/start-hyprland
%{_datadir}/bash-completion/completions/hyprctl
%{_datadir}/bash-completion/completions/hyprpm
%{_datadir}/fish/vendor_completions.d/hyprctl.fish
%{_datadir}/fish/vendor_completions.d/hyprpm.fish
%{_datadir}/hypr/
%{_datadir}/wayland-sessions/hyprland-uwsm.desktop
%{_datadir}/wayland-sessions/hyprland.desktop
%{_datadir}/xdg-desktop-portal/hyprland-portals.conf
%{_datadir}/zsh/site-functions/_hyprctl
%{_datadir}/zsh/site-functions/_hyprpm
%{_mandir}/man1/Hyprland.1*
%{_mandir}/man1/hyprctl.1*

%files devel
%{_includedir}/hyprland/
%{_datadir}/pkgconfig/hyprland.pc

%changelog
* Tue Sep 01 2026 COPR Maintainer <noreply@example.invalid> - 0.56.2-3
- Enable the optional UWSM-managed display-manager session

* Tue Sep 01 2026 COPR Maintainer <noreply@example.invalid> - 0.56.2-2
- Complete development dependencies exposed by plugin headers

* Tue Sep 01 2026 COPR Maintainer <noreply@example.invalid> - 0.56.2-1
- Initial package
