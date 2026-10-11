Name:           lua55
Version:        5.5.1
Release:        4%{?dist}
Summary:        Parallel-installable Lua 5.5 runtime for Hyprland
License:        MIT
URL:            https://github.com/lua/lua
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source1:        lua55.pc.in
Source2:        lua.hpp
Source3:        LICENSE
Source4:        gc-smoke.lua
Source5:        lua55-prefix.h
Source6:        mixed-runtime-smoke.c
Patch0:         0001-guard-negative-gc-parameter.patch

BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  binutils
BuildRequires:  pkgconfig(lua)

%description
Lua 5.5 runtime packaged under a versioned library name for Fedora releases
that need a separately maintained Lua runtime. This package does not replace
the system Lua. Public C symbols use a private namespace so embedding it
does not interpose on Fedora libraries that use the native Lua ABI.

%package devel
Summary:        Development files for the parallel Lua 5.5 runtime
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
Headers and pkg-config metadata for embedding the parallel Lua 5.5 runtime.

%prep
%autosetup -n lua-%{version} -p1
cp -p %{SOURCE3} LICENSE
cp -p %{SOURCE5} lua55-prefix.h
sed -i '/^#define lua_h/a #include "lua55-prefix.h"' lua.h
grep -F '#include "lua55-prefix.h"' lua.h

%build
%make_build -f makefile \
  CC="%{__cc}" \
  CFLAGS="%{build_cflags} -fPIC -std=c99 -DLUA_USE_LINUX" \
  MYLDFLAGS="%{build_ldflags} -Wl,-E" \
  MYLIBS="-ldl"

ar d liblua.a ltests.o
%{__cc} %{build_ldflags} -shared \
  -Wl,-soname,liblua5.5.so.1 \
  -Wl,--whole-archive liblua.a -Wl,--no-whole-archive \
  -lm -ldl -o liblua5.5.so.1.0.0

%install
install -Dpm0755 liblua5.5.so.1.0.0 \
  %{buildroot}%{_libdir}/liblua5.5.so.1.0.0
ln -s liblua5.5.so.1.0.0 %{buildroot}%{_libdir}/liblua5.5.so.1
ln -s liblua5.5.so.1 %{buildroot}%{_libdir}/liblua5.5.so

for header in lua.h luaconf.h lualib.h lauxlib.h lua55-prefix.h; do
  install -Dpm0644 "$header" "%{buildroot}%{_includedir}/lua5.5/$header"
done
install -Dpm0644 %{SOURCE2} %{buildroot}%{_includedir}/lua5.5/lua.hpp

install -d %{buildroot}%{_libdir}/pkgconfig
sed -e 's|@LIBDIR@|%{_libdir}|g' \
    -e 's|@VERSION@|%{version}|g' \
    %{SOURCE1} > %{buildroot}%{_libdir}/pkgconfig/lua55.pc

%check
./lua -e 'assert(_VERSION == "Lua 5.5")'
./lua %{SOURCE4}
# The parallel library must not export native Lua API names.
nm -D --defined-only --format=posix liblua5.5.so.1.0.0 > exported-symbols.txt
if awk '{print $1}' exported-symbols.txt | grep -E '^(lua_|luaL_|luaopen_)'; then
  echo 'Unexpected native Lua API export in parallel library' >&2
  exit 1
fi
grep -q '^lua55L_newstate ' exported-symbols.txt
%{__cc} %{build_cflags} -I. %{SOURCE6} %{build_ldflags} -ldl -o mixed-runtime-smoke
./mixed-runtime-smoke %{_libdir}/liblua.so "$PWD/liblua5.5.so.1.0.0" native-first
./mixed-runtime-smoke %{_libdir}/liblua.so "$PWD/liblua5.5.so.1.0.0" parallel-first

%files
%license LICENSE
%{_libdir}/liblua5.5.so.1
%{_libdir}/liblua5.5.so.1.0.0

%files devel
%{_includedir}/lua5.5/
%{_libdir}/liblua5.5.so
%{_libdir}/pkgconfig/lua55.pc

%changelog
* Sun Oct 11 2026 COPR Maintainer <noreply@example.invalid> - 5.5.1-4
- Isolate public C symbols from native Lua and bump the parallel library SONAME
- Check independent native/parallel states in both dynamic-loader orders

* Sun Oct 11 2026 COPR Maintainer <noreply@example.invalid> - 5.5.1-3
- Support the patched parallel runtime on both Fedora targets

* Sun Oct 11 2026 COPR Maintainer <noreply@example.invalid> - 5.5.1-2
- Backport upstream 0b29f408 to guard negative GC memory deltas
- Check ordinary incremental and generational GC behavior

* Fri Sep 18 2026 COPR Maintainer <noreply@example.invalid> - 5.5.1-1
- Update to Lua 5.5.1

* Tue Sep 01 2026 COPR Maintainer <noreply@example.invalid> - 5.5.0-1
- Add a parallel Lua 5.5 runtime for Fedora 44
