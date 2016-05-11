# WARNING: This package is synced with FC

%define lib64arches	x86_64 

%ifarch %lib64arches
    %define _lib lib64
%else
    %define _lib lib
%endif

%define _prefix /usr
%define _libdir %_prefix/%_lib
%define _bindir %_prefix/bin
%define _sysconfdir /etc
%define _datadir /usr/share
%define _defaultdocdir %_datadir/doc
%define _localstatedir /var
%define _infodir %_datadir/info

# Define directory which holds rpm config files, and some binaries actually
# NOTE: it remains */lib even on lib64 platforms as only one version
#       of rpm is supported anyway, per architecture
%define rpmdir %{_prefix}/lib/rpm

%if %{?mklibname:0}%{?!mklibname:1}
%define mklibname(ds)  %{_lib}%{1}%{?2:%{2}}%{?3:_%{3}}%{-s:-static}%{-d:-devel}
%endif

%if %{?distsuffix:0}%{?!distsuffix:1}
%define distsuffix .mga
%endif

%if %{?mkrel:0}%{?!mkrel:1}
%define mkrel(c:) %{-c: 0.%{-c*}.}%{1}%{?distsuffix:%distsuffix}%{?!distsuffix:.mga}%{?mageia_release:%mageia_release}%{?subrel:.%subrel}
%endif

%if %{?pyver:0}%{?!pyver:1}
%define pyver %(python -V 2>&1 | cut -f2 -d" " | cut -f1,2 -d".")
%endif

%define __find_requires %{rpmdir}/%{_real_vendor}/find-requires %{?buildroot:%{buildroot}} %{?_target_cpu:%{_target_cpu}}
%define __find_provides %{rpmdir}/%{_real_vendor}/find-provides

%define rpmver 4.13.0
%define snapver		rc1
%define srcver          %{rpmver}%{?snapver:-%{snapver}}
%define libver		4.12
%define libmajor	7
%define librpmname      %mklibname rpm  %{libmajor}
%define librpmnamedevel %mklibname -d rpm
%define librpmsign      %mklibname rpmsign %{libmajor}
%define librpmbuild     %mklibname rpmbuild %{libmajor}

%define rpmsetup_version 1.34

%bcond_with debug
%bcond_without python

Summary:	The RPM package management system
Name:		rpm
Epoch:		1
Version:        %{rpmver}
Release:	%mkrel %{?snapver:0.%{snapver}.}32
Group:		System/Packaging
Source:		http://www.rpm.org/releases/rpm-%{libver}.x/rpm-%{srcver}.tar.bz2
# extracted from http://pkgs.fedoraproject.org/cgit/redhat-rpm-config.git/plain/macros:
Source1:	macros.filter

#
# Fedora patches
#
# Patches already upstream:
Patch100: rpm-4.13.0-rc1-Fix-new-richdep-syntax.patch
Patch101: rpm-4.13.0-selinux--permissive-scriptlets.patch
Patch102: rpm-4.13.0-non-numeric-epoch.patch
Patch103: rpm-4.13.0-wrong-version-macro.patch
Patch104: rpm-4.13.0-memory-error.patch
Patch105: rpm-4.13.0-rpmdeps-weakdep-support.patch
Patch106: rpm-4.13.0-autopatch-fix.patch
Patch107: rpm-4.13.0-ignore-sigpipe.patch
Patch108: rpm-4.13.0-unsupported-keys.patch
Patch109: rpm-4.13.0-fix-crash-on-corrupted.patch
Patch110: rpm-4.13.0-disabling-filetriggers.patch
Patch111: rpm-4.13.0-chroot-file-triggers.patch
Patch112: rpm-4.13.0-missingok.patch
Patch113: rpm-4.13.0-recursing-rpmdeps.patch
Patch114: rpm-4.13.0-autosetup-errors.patch
Patch115: rpm-4.13.0-unlimited-macro-expand.patch
Patch116: rpm-4.13.0-idle-and-sleep-in-systemd-inhibit.patch
Patch117: rpm-4.13.0-add-mipsr6-support.patch
Patch118: rpm-4.13.0-Use-pkg-dpaths-during-dependency-generation.patch
Patch119: rpm-4.13.0-Noarch-ExclusiveArch.patch
Patch120: rpm-4.13.0-redirect2null.patch
Patch121: rpm-4.13.0-lang-doc-directives.patch
Patch122: rpm-4.13.0-elem-progress-callback.patch
Patch123: rpm-4.13.0-weak-rich-consistency.patch
Patch124: rpm-4.13.0-fuzz-settings.patch
Patch125: rpm-4.13.0-patch-flags.patch
Patch126: rpm-4.13.0-no-backup-if-mismatch.patch
Patch127: rpm-4.13.0-rpmtd-out-of-bounds.patch
Patch128: rpm-4.13.0-stringFormat-sigsegv.patch

# These are not yet upstream
Patch302: rpm-4.7.1-geode-i686.patch
# Probably to be upstreamed in slightly different form
Patch304: rpm-4.9.1.1-ld-flags.patch
# Compressed debuginfo support (#833311)
Patch305: rpm-4.10.0-dwz-debuginfo.patch
# Minidebuginfo support (#834073)
Patch306: rpm-4.10.0-minidebuginfo.patch
# (tv) Disabled as it breaks SUID (mga#14691):
# Fix CRC32 after dwz (#971119)
#Patch307: rpm-4.11.1-sepdebugcrcfix.patch
# Fix race condidition where unchecked data is exposed in the file system
Patch308: rpm-4.12.0.x-CVE-2013-6435.patch
# Add check against malicious CPIO file name size
Patch309: rpm-4.12.0.x-CVE-2014-8118.patch

#
# Mageia patches
#

# In original rpm, -bb --short-circuit does not work and run all stage
# From popular request, we allow to do this
# http://qa.mandriva.com/show_bug.cgi?id=15896
Patch70:	rpm-4.12.90-bb-shortcircuit.patch

# don't conflict for doc files
# (to be able to install lib*-devel together with lib64*-devel even if they have conflicting manpages)
Patch83: rpm-4.12.0-no-doc-conflicts.patch

# Fix http://qa.mandriva.com/show_bug.cgi?id=19392
# (is this working??)
Patch84: rpm-4.4.2.2-rpmqv-ghost.patch

# [Dec 2008] macrofiles from rpmrc does not overrides MACROFILES anymore
# Upstream 4.11 will have /usr/lib/rpm/macros.d:
Patch144: rpm-4.9.0-read-macros_d-dot-macros.patch

# without this patch, "#%%define foo bar" is surprisingly equivalent to "%%define foo bar"
# with this patch, "#%%define foo bar" is a fatal error
# Bug still valid => Send upstream for review.
Patch145: rpm-forbid-badly-commented-define-in-spec.patch

# (nb: see the patch for more info about this issue)
#Patch151: rpm-4.6.0-rc1-protect-against-non-robust-futex.patch

# Introduce (deprecated) %%apply_patches:
# (To be dropped once all pkgs are converted to %%auto_setup)
Patch157: rpm-4.10.1-introduce-_after_setup-which-is-called-after-setup.patch
Patch159: introduce-apply_patches-and-lua-var-patches_num.patch

#
# Merge mageia's perl.prov improvements back into upstream:
#
# making sure automatic provides & requires for perl package are using the new
# macro %%perl_convert_version:
Patch162: use_perl_convert_version.diff

#
# Merge mageia's find-requires.sh improvements back into upstream:
#
# (tv) output perl-base requires instead of /usr/bin/perl with internal generator:
# (ngompa) This patch can be dropped once we switch fully over to dnf
Patch170: script-perl-base.diff
# (tv) do not emit requires for /bin/sh (required by glibc) or interpreters for which
# we have custom
Patch172: script-filtering.diff
# (tv) "resolve" /bin/env foo interpreter to actual path, rather than generating
# dependencies on coreutils, should trim off ~800 dependencies more
Patch173: script-env.diff
# (tv) output pkgconfig requires instead of /usr/bin/pkgconfig with internal generator:
# (ngompa) This patch can be dropped once we switch fully over to dnf
Patch174: pkgconfig.diff
# (tv) no not emit "rtld(GNU_HASH)" requires as we've support for it since mga1:
# (saves ~5K packages' dependency in synthesis)
Patch175: no-rtld_GNU_HASH_req.diff
# (tv) replace file deps by requires on packages (when interp is installed):
# (ngompa) This patch can be dropped once we switch fully over to dnf
Patch176: script-no-file-deps.diff
# (tv) replace file deps by requires on packages (common cases for !BRed interp):
# (ngompa) This patch can be dropped once we switch fully over to dnf
Patch177: script-no-file-deps2.diff
# (pt) generate ELF provides for libraries, not only for executables
Patch180: elf_libs_req.diff 
# [Suse]add --assumeexec option for previous patch:
Patch181: assumeexec.diff 
# (tv) fix memleak in file triggers (UPSTREAM):
Patch190: 0001-Fix-memory-leak-in-file-triggers.patch

# (tv) rename cloberred %%configure as %%old_configure:
Patch200: rpm_configure.diff

# (tv) fix segfault in perl-RPM4's testsuite:
Patch201: 0001-fix-segfault-when-calling-with-args-NULL.patch

# Automatically handle ruby gem extraction in %%setup:
Patch2006: rpm-4.12.90-setup-rubygems.patch

# Various arch enabling:
Patch3003: rpm_arm_mips_isa_macros.patch
Patch3004: rpm_add_armv5tl.patch


# Mageia patches that are easier to rediff on top of FC patches:
#---------------------------------------------------------------
# (tv) merge mga stuff from rpm-setup:
# (for spec-helper)
Patch4000: rpm-4.10.0-find-debuginfo__mga-cfg.diff

# 2 patches to drop in mga7:
# (tv) make old suggests be equivalent to recommends (RECOMMENDNAME -> OLDSUGGEST):
Patch4010: rpm-4.12.0-oldsuggest_equals_recommends.patch
# (tv) uneeeded: maps RECOMMENDNEVR to OLDSUGGEST instead of OLDRECOMMEND
Patch4012: rpm-mga-suggests.diff

# (Debian): avoid useless) linking (&dependency) on all supported python versions:
Patch6001: do-not-link-libpython.patch

License:	GPLv2+
BuildRequires:	autoconf
BuildRequires:	pkgconfig(zlib)
BuildRequires:  bzip2-devel
BuildRequires:	pkgconfig(liblzma) >= 5
BuildRequires:	automake
BuildRequires:	doxygen
BuildRequires:	elfutils-devel
BuildRequires:	libbeecrypt-devel
#BuildRequires:	binutils-devel
BuildRequires:	ed
BuildRequires:	gettext-devel
BuildRequires:  pkgconfig(sqlite3)
BuildRequires:  db5.3-devel
BuildRequires:  pkgconfig(dbus-1)
BuildRequires:  pkgconfig(neon)
BuildRequires:	pkgconfig(popt)
BuildRequires:	pkgconfig(nss)
BuildRequires:	magic-devel
BuildRequires:  rpm-%{_real_vendor}-setup-build %{?rpmsetup_version:>= %{rpmsetup_version}}
BuildRequires:  readline-devel
BuildRequires:	pkgconfig(ncurses)
BuildRequires:  pkgconfig(libssl)
BuildRequires:  pkgconfig(lua) >= 5.2.3-3.mga5
BuildRequires:  pkgconfig(libcap)
BuildRequires:  pkgconfig(libarchive)
# Needed for doc
#BuildRequires:	graphviz
BuildRequires:	tetex
%if %with python
BuildRequires:  pkgconfig(python)
BuildRequires:  pkgconfig(python-3.5)
%endif
# for testsuite:
BuildRequires: eatmydata
BuildRequires: fakechroot

Requires:	bzip2 >= 0.9.0c-2
Requires:	xz
Requires:	cpio
Requires:	gawk
Requires:	mktemp
Requires:	setup >= 2.2.0-8
Requires:	rpm-%{_real_vendor}-setup >= 1.85
Requires:	update-alternatives
Requires:	%librpmname = %epoch:%version-%release
URL:            http://rpm.org/
%define         git_url        http://rpm.org/git/rpm.git
Requires(pre):		rpm-helper
Requires(pre):		coreutils
Requires(postun):	rpm-helper

Conflicts: perl-URPM < 4.0-2.mga3
Conflicts: jpackage-utils < 1:1.7.5-17
# fix for plugins conflict:
Conflicts: %{_lib}rpm3 < 1:4.12.0.1-20.3

%description
RPM is a powerful command line driven package management system capable of
installing, uninstalling, verifying, querying, and updating software packages.
Each software package consists of an archive of files along with information
about the package like its version, a description, etc.

%package   -n %librpmbuild
Summary:   Libraries for building and signing RPM packages
Group:     System/Libraries
Obsoletes: rpm-build-libs%{_isa} < %{version}-%{release}
Provides: rpm-build-libs%{_isa} = %{version}-%{release}

%description -n %librpmbuild
This package contains the RPM shared libraries for building and signing
packages.

%package  -n %librpmsign
Summary:  Libraries for building and signing RPM packages
Group:    System/Libraries

%description -n %librpmsign
This package contains the RPM shared libraries for building and signing
packages.

%package -n %librpmname
Summary:  Library used by rpm
Group:	  System/Libraries
Provides: librpm = %version-%release
# for fixed lua:
Requires:  %{mklibname lua 5.2} >= 5.2.3-3.mga5
Provides: rpm-libs = %version-%release

%description -n %librpmname
RPM is a powerful command line driven package management system capable of
installing, uninstalling, verifying, querying, and updating software packages.
This package contains common files to all applications based on rpm.

%package -n %librpmnamedevel
Summary:	Development files for applications which will manipulate RPM packages
Group:		Development/C
Requires:	rpm = %epoch:%{version}-%{release}
Provides:	librpm-devel = %version-%release
Provides:   	rpm-devel = %version-%release
Requires:       %librpmname = %epoch:%version-%release
Requires:       %librpmbuild = %epoch:%version-%release
Requires:       %librpmsign = %epoch:%version-%release

%description -n %librpmnamedevel
This package contains the RPM C library and header files.  These
development files will simplify the process of writing programs
which manipulate RPM packages and databases and are intended to make
it easier to create graphical package managers or any other tools
that need an intimate knowledge of RPM packages in order to function.

This package should be installed if you want to develop programs that
will manipulate RPM packages and databases.

%package build
Summary:	Scripts and executable programs used to build packages
Group:		System/Packaging
Requires:	autoconf
Requires:	automake
Requires:	file
Requires:	gcc-c++
# We need cputoolize & amd64-* alias to x86_64-* in config.sub
Requires:	libtool-base
Requires:	patch
Requires:	make
Requires:	tar
Requires:	unzip
Requires:	elfutils
Requires:	perl(CPAN::Meta) >= 2.112.150
Requires:	perl(ExtUtils::MakeMaker) >= 6.570_700
Requires:       perl(YAML::Tiny)
Requires:	rpm = %epoch:%{version}-%{release}
Requires:	rpm-%{_real_vendor}-setup-build %{?rpmsetup_version:>= %{rpmsetup_version}}
Requires:	%librpmbuild = %epoch:%version

%description build
This package contains scripts and executable programs that are used to
build packages using RPM.

%package doc
Summary: RPM Documentation
Group:   Documentation
BuildArch: noarch

%description doc
This package contains the RPM documentation.

%package sign
Summary: Package signing support
Group:   System/Base

%description sign
This package contains support for digitally signing RPM packages.

%if %with python
%package -n python-rpm
Summary:	Python 2 bindings for apps which will manipulate RPM packages
Group:		Development/Python
Requires:	rpm = %epoch:%{version}-%{release}

%description -n python-rpm
The rpm-python package contains a module which permits applications
written in the Python programming language to use the interface
supplied by RPM (RPM Package Manager) libraries.

This package should be installed if you want to develop Python 2
programs that will manipulate RPM packages and databases.

%package -n python3-rpm
Summary:	Python 3 bindings for apps which will manipulate RPM packages
Group:		Development/Python
Requires:	rpm = %epoch:%{version}-%{release}

%description -n python3-rpm
The rpm-python package contains a module which permits applications
written in the Python programming language to use the interface
supplied by RPM (RPM Package Manager) libraries.

This package should be installed if you want to develop Python 3
programs that will manipulate RPM packages and databases.
%endif

%prep
%setup -q -n %name-%srcver
%autopatch -p1

%build
%define _disable_ld_no_undefined 1
aclocal
automake-1.14 --add-missing
automake
autoreconf

%if %with debug
RPM_OPT_FLAGS=-g
%endif
export CPPFLAGS="$CPPFLAGS `pkg-config --cflags nss`"
CFLAGS="$RPM_OPT_FLAGS -fPIC" CXXFLAGS="$RPM_OPT_FLAGS -fPIC" \
    %configure2_5x \
        --localstatedir=%{_var} \
        --sharedstatedir=%{_var}/lib \
        --enable-nls \
        --enable-sqlite3 \
        --without-javaglue \
        %{?_with_debug} \
        --with-external-db \
        %{?_with_python} \
        --with-glob \
        --without-selinux \
        --with-apidocs \
        --with-cap

%make
%if %with python
pushd python
%{__python} setup.py build
%{__python3} setup.py build
popd
%endif

%install
%makeinstall_std

%if %with python
# We need to build with --enable-python for the self-test suite, but we
# actually package the bindings built with setup.py (#531543#c26)
rm -rf $RPM_BUILD_ROOT/%{python_sitearch}
pushd python
%{__python} setup.py install --skip-build --root $RPM_BUILD_ROOT
%{__python3} setup.py install --skip-build --root $RPM_BUILD_ROOT
popd
%endif

find $RPM_BUILD_ROOT -name "*.la"|xargs rm -f

# Save list of packages through cron
mkdir -p ${RPM_BUILD_ROOT}/etc/cron.daily
install -m 755 scripts/rpm.daily ${RPM_BUILD_ROOT}/etc/cron.daily/rpm

mkdir -p ${RPM_BUILD_ROOT}/etc/logrotate.d
install -m 644 scripts/rpm.log ${RPM_BUILD_ROOT}/etc/logrotate.d/rpm

mkdir -p $RPM_BUILD_ROOT/var/lib/rpm
for dbi in \
	Basenames Conflictname Dirnames Group Installtid Name Providename \
	Provideversion Removetid Requirename Requireversion Triggername \
	Obsoletename Packages Sha1header Sigmd5 __db.001 __db.002 \
	__db.003 __db.004 __db.005 __db.006 __db.007 __db.008 __db.009
do
    touch $RPM_BUILD_ROOT/var/lib/rpm/$dbi
done

test -d doc-copy || mkdir doc-copy
rm -rf doc-copy/*
ln -f doc/manual/* doc-copy/
rm -f doc-copy/Makefile*

mkdir -p $RPM_BUILD_ROOT/var/spool/repackage

mkdir -p %buildroot%rpmdir/macros.d
install %SOURCE1 %buildroot%rpmdir/macros.d
mkdir -p %buildroot%_sysconfdir/rpm/macros.d
cat > %buildroot%_sysconfdir/rpm/macros <<EOF
# Put your own system macros here
# usually contains 

# Set this one according your locales
# %%_install_langs

EOF

%{rpmdir}/%{_host_vendor}/find-lang.pl $RPM_BUILD_ROOT %{name}

%check
exit 0
eatmydata make check
[ "$(ls -A tests/rpmtests.dir)" ] && cat tests/rpmtests.log

%pre
/usr/share/rpm-helper/add-user rpm $1 rpm /var/lib/rpm /bin/false

rm -rf /usr/lib/rpm/*-mandrake-*
rm -rf /usr/lib/rpm/*-%{_real_vendor}-*


%post
# nuke __db.00? when updating to this rpm
rm -f /var/lib/rpm/__db.00?

if [ ! -f /var/lib/rpm/Packages ]; then
    /bin/rpm --initdb
fi

%postun
/usr/share/rpm-helper/del-user rpm $1 rpm

%define	rpmattr		%attr(0755, rpm, rpm)

%files -f %{name}.lang
%doc GROUPS CHANGES doc/manual/[a-z]*
%attr(0755,rpm,rpm) /bin/rpm
%attr(0755, rpm, rpm) %{_bindir}/rpm2cpio
%attr(0755, rpm, rpm) %{_bindir}/rpm2archive
%attr(0755, rpm, rpm) %{_bindir}/gendiff
%attr(0755, rpm, rpm) %{_bindir}/rpmdb
%attr(0755, rpm, rpm) %{_bindir}/rpmkeys
%attr(0755, rpm, rpm) %{_bindir}/rpmgraph
%{_bindir}/rpmquery
%{_bindir}/rpmverify
%{_libdir}/rpm-plugins

%dir %{_localstatedir}/spool/repackage
%dir %{rpmdir}
%dir /etc/rpm
%config(noreplace) /etc/rpm/macros
%dir /etc/rpm/macros.d
%attr(0755, rpm, rpm) %{rpmdir}/config.guess
%attr(0755, rpm, rpm) %{rpmdir}/config.sub
%attr(0755, rpm, rpm) %{rpmdir}/rpmdb_*
%attr(0644, rpm, rpm) %{rpmdir}/macros
%rpmdir/macros.d
%attr(0755, rpm, rpm) %{rpmdir}/mkinstalldirs
%attr(0755, rpm, rpm) %{rpmdir}/rpm.*
%attr(0644, rpm, rpm) %{rpmdir}/rpmpopt*
%attr(0644, rpm, rpm) %{rpmdir}/rpmrc
%attr(0755, rpm, rpm) %{rpmdir}/elfdeps
%attr(0755, rpm, rpm) %{rpmdir}/script.req

%rpmattr	%{rpmdir}/rpm2cpio.sh
%rpmattr	%{rpmdir}/tgpg

%dir %attr(   -, rpm, rpm) %{rpmdir}/fileattrs
%attr(0644, rpm, rpm) %{rpmdir}/fileattrs/*.attr

%dir %attr(   -, rpm, rpm) %{rpmdir}/platform/
%exclude %{rpmdir}/platform/m68k-linux/macros
%ifarch %{ix86} x86_64
%attr(   -, rpm, rpm) %{rpmdir}/platform/i*86-*
%attr(   -, rpm, rpm) %{rpmdir}/platform/athlon-*
%attr(   -, rpm, rpm) %{rpmdir}/platform/pentium*-*
%attr(   -, rpm, rpm) %{rpmdir}/platform/geode-*
%else
%exclude %{rpmdir}/platform/i*86-linux/macros
%exclude %{rpmdir}/platform/athlon-linux/macros
%exclude %{rpmdir}/platform/pentium*-linux/macros
%exclude %{rpmdir}/platform/geode-linux/macros
%endif
%ifarch x86_64
%attr(   -, rpm, rpm) %{rpmdir}/platform/amd64-*
%attr(   -, rpm, rpm) %{rpmdir}/platform/x86_64-*
%attr(   -, rpm, rpm) %{rpmdir}/platform/ia32e-*
%else
%exclude %{rpmdir}/platform/amd64-linux/macros
%exclude %{rpmdir}/platform/ia32e-linux/macros
%exclude %{rpmdir}/platform/x86_64-linux/macros
%endif
%ifarch %arm
%attr(   -, rpm, rpm) %{rpmdir}/platform/arm*
%attr(   -, rpm, rpm) %{rpmdir}/platform/aarch64*/macros
%else
%exclude %{rpmdir}/platform/arm*/macros
%exclude %{rpmdir}/platform/aarch64*/macros
%endif
%attr(   -, rpm, rpm) %{rpmdir}/platform/noarch*
# new in 4.10.0:
%exclude %{rpmdir}/platform/alpha*-linux/macros
%exclude %{rpmdir}/platform/sparc*-linux/macros
%exclude %{rpmdir}/platform/ia64*-linux/macros
%exclude %{rpmdir}/platform/m68k*-linux/macros
%exclude %{rpmdir}/platform/mips*-linux/macros
%exclude %{rpmdir}/platform/ppc*-linux/macros
%exclude %{rpmdir}/platform/s390*-linux/macros
%exclude %{rpmdir}/platform/sh*-linux/macros



%{_mandir}/man[18]/*.[18]*
%lang(pl) %{_mandir}/pl/man[18]/*.[18]*
%lang(ru) %{_mandir}/ru/man[18]/*.[18]*
%lang(ja) %{_mandir}/ja/man[18]/*.[18]*
%lang(sk) %{_mandir}/sk/man[18]/*.[18]*
%lang(fr) %{_mandir}/fr/man[18]/*.[18]*
%lang(ko) %{_mandir}/ko/man[18]/*.[18]*

%config(noreplace,missingok)	/etc/cron.daily/rpm
%config(noreplace,missingok)	/etc/logrotate.d/rpm

%attr(0755, rpm, rpm)	%dir %_localstatedir/lib/rpm

%define	rpmdbattr %attr(0644, rpm, rpm) %verify(not md5 size mtime) %ghost %config(missingok,noreplace)

%rpmdbattr	/var/lib/rpm/Basenames
%rpmdbattr	/var/lib/rpm/Conflictname
%rpmdbattr	/var/lib/rpm/__db.0*
%rpmdbattr	/var/lib/rpm/Dirnames
%rpmdbattr	/var/lib/rpm/Group
%rpmdbattr	/var/lib/rpm/Installtid
%rpmdbattr	/var/lib/rpm/Name
%rpmdbattr	/var/lib/rpm/Obsoletename
%rpmdbattr	/var/lib/rpm/Packages
%rpmdbattr	/var/lib/rpm/Providename
%rpmdbattr	/var/lib/rpm/Provideversion
%rpmdbattr	/var/lib/rpm/Removetid
%rpmdbattr	/var/lib/rpm/Requirename
%rpmdbattr	/var/lib/rpm/Requireversion
%rpmdbattr	/var/lib/rpm/Sha1header
%rpmdbattr	/var/lib/rpm/Sigmd5
%rpmdbattr	/var/lib/rpm/Triggername

%files build
%doc CHANGES
%doc doc-copy/*
%rpmattr	%{_bindir}/rpmbuild
%rpmattr        %{_bindir}/rpmspec
%rpmattr	%{_prefix}/lib/rpm/brp-*
%rpmattr	%{_prefix}/lib/rpm/check-files
%rpmattr	%{_prefix}/lib/rpm/debugedit
%rpmattr	%{_prefix}/lib/rpm/*.prov 
%rpmattr	%{_prefix}/lib/rpm/find-debuginfo.sh
%rpmattr	%{_prefix}/lib/rpm/find-lang.sh
%rpmattr	%{_prefix}/lib/rpm/find-provides
%rpmattr	%{_prefix}/lib/rpm/find-requires
%rpmattr	%{_prefix}/lib/rpm/perl.req

%rpmattr	%{_prefix}/lib/rpm/check-buildroot
%rpmattr	%{_prefix}/lib/rpm/check-prereqs
%rpmattr	%{_prefix}/lib/rpm/check-rpaths
%rpmattr	%{_prefix}/lib/rpm/check-rpaths-worker
%rpmattr	%{_prefix}/lib/rpm/libtooldeps.sh
%rpmattr	%{_prefix}/lib/rpm/macros.perl
%rpmattr	%{_prefix}/lib/rpm/macros.php
%rpmattr	%{_prefix}/lib/rpm/macros.python
%rpmattr	%{_prefix}/lib/rpm/mono-find-provides
%rpmattr	%{_prefix}/lib/rpm/mono-find-requires
%rpmattr	%{_prefix}/lib/rpm/ocaml-find-provides.sh
%rpmattr	%{_prefix}/lib/rpm/ocaml-find-requires.sh
%rpmattr	%{_prefix}/lib/rpm/pkgconfigdeps.sh

%rpmattr	%{_prefix}/lib/rpm/rpmdeps
%rpmattr        %{_prefix}/lib/rpm/pythondeps.sh


%{_mandir}/man8/rpmbuild.8*
%{_mandir}/man8/rpmdeps.8*

%if %with python
%files -n python-rpm
%{python_sitearch}/rpm
%{python_sitearch}/rpm_python-%{version}%{?snapver:_%{snapver}}-py*.egg-info

%files -n python3-rpm
%defattr(-,root,root)
%{python3_sitearch}/rpm
%{python3_sitearch}/rpm_python-%{version}%{?snapver:_%{snapver}}-py%{python3_version}.egg-info
%endif

%files -n %librpmname
%{_libdir}/librpm.so.%{libmajor}*
%{_libdir}/librpmio.so.%{libmajor}*

%files -n %librpmbuild
%{_libdir}/librpmbuild.so.%{libmajor}*

%files -n %librpmsign
%{_libdir}/librpmsign.so.%{libmajor}*

%files doc
%doc doc/librpm/html

%files sign
%{_bindir}/rpmsign
%{_mandir}/man8/rpmsign.8*

%files -n %librpmnamedevel
%{_includedir}/rpm
%{_libdir}/librpm.so
%{_libdir}/librpmio.so
%{_libdir}/librpmbuild.so
%{_libdir}/librpmsign.so
%{_libdir}/pkgconfig/rpm.pc

