Name:           uwsm
Version:        0.26.7
Release:        1%{?dist}
Summary:        Universal Wayland Session Manager
License:        MIT
URL:            https://github.com/Vladimir-csp/uwsm
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  desktop-file-utils
BuildRequires:  meson >= 1.3.0
BuildRequires:  python3-dbus
BuildRequires:  python3-devel >= 3.10
BuildRequires:  python3-pyxdg
BuildRequires:  scdoc
BuildRequires:  systemd-rpm-macros

Requires:       python3-dbus
Requires:       python3-pyxdg
Requires:       systemd
Requires:       util-linux
Recommends:     dbus-broker
Suggests:       inotify-tools
Suggests:       libnotify
Suggests:       newt

%description
UWSM provides systemd user units and helpers for launching and managing
standalone Wayland compositor sessions. It includes integration for Hyprland
and tools for launching applications in graphical-session slices.

%prep
%autosetup -p1

%build
%meson \
  -Dcanonicalize-bins=enabled \
  -Duuctl=enabled \
  -Dfumon=enabled \
  -Dfumon-preset=disabled \
  -Dttyautolock=enabled \
  -Dttyautolock-preset=disabled \
  -Dwait-tray=enabled \
  -Duwsm-app=enabled
%meson_build

%install
%meson_install
touch -r uwsm/main.py \
  %{buildroot}%{_datadir}/uwsm/modules/uwsm/params.py
ln -s uwsm-app.1 %{buildroot}%{_mandir}/man1/uwsm-terminal.1
ln -s uwsm-app.1 %{buildroot}%{_mandir}/man1/uwsm-terminal-scope.1
ln -s uwsm-app.1 %{buildroot}%{_mandir}/man1/uwsm-terminal-service.1

%check
PYTHONPATH=%{buildroot}%{_datadir}/uwsm/modules \
  %{buildroot}%{_bindir}/uwsm --version
desktop-file-validate %{buildroot}%{_datadir}/applications/uuctl.desktop
find %{buildroot}%{_libexecdir}/uwsm %{buildroot}%{_datadir}/uwsm/plugins \
  -type f -name '*.sh' -exec sh -n '{}' +

%files
%license %{_licensedir}/%{name}/LICENSE
%doc %{_docdir}/%{name}/README.md
%doc %{_docdir}/%{name}/example-units/
%{_bindir}/fumon
%{_bindir}/ttyautolock
%{_bindir}/uuctl
%{_bindir}/uwsm
%{_bindir}/uwsm-app
%{_bindir}/uwsm-terminal
%{_bindir}/uwsm-terminal-scope
%{_bindir}/uwsm-terminal-service
%{_bindir}/wait-tray
%{_libexecdir}/uwsm/
%{_datadir}/applications/uuctl.desktop
%{_datadir}/uwsm/
%{_userunitdir}/app-graphical.slice
%{_userunitdir}/background-graphical.slice
%{_userunitdir}/fumon.service
%{_userunitdir}/session-graphical.slice
%{_userunitdir}/ttyautolock@.service
%{_userunitdir}/wayland-session-bindpid@.service
%{_userunitdir}/wayland-session-envelope@.target
%{_userunitdir}/wayland-session-pre@.target
%{_userunitdir}/wayland-session-shutdown.target
%{_userunitdir}/wayland-session-waitenv.service
%{_userunitdir}/wayland-session-xdg-autostart@.target
%{_userunitdir}/wayland-session@.target
%{_userunitdir}/wayland-wm-app-daemon.service
%{_userunitdir}/wayland-wm-env@.service
%{_userunitdir}/wayland-wm@.service
%{_userpresetdir}/80-fumon.preset
%{_userpresetdir}/80-ttyautolock.preset
%{_mandir}/man1/fumon.1*
%{_mandir}/man1/ttyautolock.1*
%{_mandir}/man1/uuctl.1*
%{_mandir}/man1/uwsm-app.1*
%{_mandir}/man1/uwsm-terminal.1*
%{_mandir}/man1/uwsm-terminal-scope.1*
%{_mandir}/man1/uwsm-terminal-service.1*
%{_mandir}/man1/uwsm.1*
%{_mandir}/man3/uwsm-plugins.3*

%changelog
* Tue Sep 01 2026 COPR Maintainer <noreply@example.invalid> - 0.26.7-1
- Initial package
