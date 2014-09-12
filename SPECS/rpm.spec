%define lib64arches	x86_64 
%define lib64oses	linux

%ifarch %lib64arches
%ifos %lib64oses
    %define _lib lib64
%else
    %define _lib lib
%endif
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

%if %{?apply_patches:0}%{?!apply_patches:1}
%define apply_patches %(for p in `grep '^Patch.*:' "%{_specdir}/rpm.spec" | cut -d':' -f2-`; do echo "patch -p1 -F0 -i %{_sourcedir}/$p"; done )
%endif

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

%if %{?mips:0}%{?!mips:1}
%define mips		mips mipsel mips32 mips32el mips64 mips64el
%endif

%if %{?pyver:0}%{?!pyver:1}
%define pyver %(python -V 2>&1 | cut -f2 -d" " | cut -f1,2 -d".")
%endif

%define __find_requires %{rpmdir}/%{_real_vendor}/find-requires %{?buildroot:%{buildroot}} %{?_target_cpu:%{_target_cpu}}
%define __find_provides %{rpmdir}/%{_real_vendor}/find-provides

%define snapver		rc1
%define rpmversion	4.12.0
%define srcver          %{rpmversion}%{?snapver:-%{snapver}}
%define libver		4.10
%define libmajor	3
%define librpmname      %mklibname rpm  %{libmajor}
%define librpmnamedevel %mklibname -d rpm
%define librpmsign      %mklibname rpmsign %{libmajor}
%define librpmbuild     %mklibname rpmbuild %{libmajor}

%define buildpython 1
%define rpmsetup_version 1.34

%define builddebug 0
%{?_with_debug:%define builddebug 1}

%{?_with_python:%define buildpython 1}
%{?_without_python:%define buildpython 0}

# disable plugins initially
%define buildplugins 1
%{?_with_plugins:%define buildplugins 1}

Summary:	The RPM package management system
Name:		rpm
Epoch:		1
Version:        %{rpmversion}
Release:	%mkrel %{?snapver:0.%{snapver}.}1
Group:		System/Packaging
Source:		http://www.rpm.org/releases/rpm-%{libver}.x/rpm-%{srcver}.tar.bz2
# Add some undocumented feature to gendiff
# Send upstream ? drop ?
Patch17:	rpm-4.4.2.2-gendiff-improved.patch

# if %post of foo-2 fails,
# or if %preun of foo-1 fails,
# or if %postun of foo-1 fails,
# => foo-1 is not removed, so we end up with both packages in rpmdb
# this patch makes rpm ignore the error in those cases
# failing %pre must still make the rpm install fail (mdv #23677)
#
# (nb: the exit code for pretrans/posttrans & trigger/triggerun/triggerpostun
#       scripts is ignored with or without this patch)
# Needed for urpmi testsuite:
Patch22:        rpm-4.12.0-non-pre-scripts-dont-fail.patch

# (fredl) add loging facilities through syslog (pushed upstream, might be replaced by a rpm plugin in 4.12):
#Patch31:	rpm-4.9.0-syslog.patch

# - force /usr/lib/rpm/mageia/rpmrc instead of /usr/lib/rpm/<vendor>/rpmrc
# - read /usr/lib/rpm/mageia/rpmpopt (not only /usr/lib/rpm/rpmpopt)
# if we deprecated the use of rpm -ba , ...,  we can get rid of this patch
Patch64:    rpm-4.9.1.1-mageia-rpmrc-rpmpopt.patch

# In original rpm, -bb --short-circuit does not work and run all stage
# From popular request, we allow to do this
# http://qa.mandriva.com/show_bug.cgi?id=15896
Patch70:	rpm-4.9.1-bb-shortcircuit.patch

# don't conflict for doc files
# (to be able to install lib*-devel together with lib64*-devel even if they have conflicting manpages)
Patch83: rpm-4.12.0-no-doc-conflicts.patch

# Fix http://qa.mandriva.com/show_bug.cgi?id=19392
# (is this working??)
Patch84: rpm-4.4.2.2-rpmqv-ghost.patch

# Fix diff issue when buildroot contains some "//"
Patch111: rpm-check-file-trim-double-slash-in-buildroot.patch

# [Dec 2008] macrofiles from rpmrc does not overrides MACROFILES anymore
# Upstream 4.11 will have /usr/lib/rpm/macros.d:
Patch114: rpm-4.9.0-read-macros_d-dot-macros.patch

# [pixel] without this patch, "rpm -e" or "rpm -U" will need to stat(2) every dirnames of
# files from the package (eg COPYING) in the db. This is quite costly when not in cache 
# (eg on a test here: >300 stats, and so 3 seconds after a "echo 3 > /proc/sys/vm/drop_caches")
# this breaks urpmi test case test_rpm_i_fail('gd') in superuser--file-conflicts.t,
# but this is bad design anyway
#Patch124: rpm-4.6.0-rc1-speedup-by-not-checking-same-files-with-different-paths-through-symlink.patch

# (from Turbolinux) remove a wrong check in case %_topdir is /RPM (ie when it is short)
# Panu said: "To my knowledge this is a true technical limitation of the
# implementation: as long as debugedit can just overwrite data in the elf
# sections things keep relatively easy, but if dest_dir is longer than the
# original directory, debugedit would have to expand the whole elf file. Which
# might be technically possible but debugedit currently does not even try to."
Patch135: rpm-4.12.0-fix-debugedit.patch

# without this patch, "#%define foo bar" is surprisingly equivalent to "%define foo bar"
# with this patch, "#%define foo bar" is a fatal error
# Bug still valid => Send upstream for review.
Patch145: rpm-forbid-badly-commented-define-in-spec.patch

# cf http://wiki.mandriva.com/en/Rpm_filetriggers
Patch146: rpm-4.12.0-filetriggers.patch
Patch147: rpm-4.11.1-filetriggers-priority.patch
Patch148: rpm-4.11.1-filetriggers-warnings.patch

# (nb: see the patch for more info about this issue)
#Patch151: rpm-4.6.0-rc1-protect-against-non-robust-futex.patch

Patch157: rpm-4.10.1-introduce-_after_setup-which-is-called-after-setup.patch
#Patch158: introduce-_patch-and-allow-easy-override-when-the-p.patch
Patch159: introduce-apply_patches-and-lua-var-patches_num.patch

#
# Merge mageia's perl.prov improvements back into upstream:
#
# ignore .pm files for perl provides
Patch160: ignore-non-perl-modules.diff
# making sure automatic provides & requires for perl package are using the new
# macro %perl_convert_version:
Patch162: use_perl_convert_version.diff
# skip plain, regular comments:
Patch163: skip-plain-regular-comments.diff
# support for _ in perl module version:
Patch164: support-for-_-in-perl-module-version.diff

#
# Merge mageia's find-requires.sh improvements back into upstream:
#
# (tv) output perl-base requires instead of /usr/bin/perl with internal generator:
Patch170: script-perl-base.diff
# (tv) do not emit requires for /bin/sh (required by glibc) or interpreters for which
# we have custom
Patch172: script-filtering.diff
# (tv) "resolve" /bin/env foo interpreter to actual path, rather than generating
# dependencies on coreutils, should trim off ~800 dependencies more
Patch173: script-env.diff
# (tv) output pkgconfig requires instead of /usr/bin/pkgconfig.diff with internal generator:
Patch174: pkgconfig.diff
# (tv) no not emit "rtld(GNU_HASH)" requires as we've support for it since mga1:
# (saves ~5K packages' dependency in synthesis)
Patch175: no-rtld_GNU_HASH_req.diff

Patch1007: rpm-4.12.0-xz-support.patch

# Prevents $DOCDIR from being wiped out when using %%doc <fileinbuilddir>,
# as this breaks stuff that installs files to $DOCDIR during %%install
#Patch1008: rpm-4.6.0-rc3-no_rm_-rf_DOCDIR.patch

# Turbolinux patches
# Crusoe CPUs say that their CPU family is "5" but they have enough features for i686.
Patch2003: rpm-4.4.2.3-rc1-transmeta-crusoe-is-686.patch

Patch2006: rpm-4.10.0-setup-rubygems.patch

# (tv) fix tests:
Patch2100: rpm-4.11.1-fix-testsuite.diff

Patch3000: mips_macros.patch
Patch3002: mips_define_isa_macros.patch
Patch3003: rpm_arm_mips_isa_macros.patch
Patch3004: rpm_add_armv5tl.patch

# when using fakechroot, make sure that testsuite pathes are against /
# and not full path
Patch3005: rpm-4.12.0-fix-testsuite-pathes.patch

#
# Fedora patches
# Patches 41xx are already in upstream and are 1xx in FC
#
# (tv) Temporary Patch to provide support for updates (FC):
Patch3500: rpm-4.10.90-rpmlib-filesystem-check.patch
# (tv) Compressed debuginfo support (UPSTREAM):
Patch3501: rpm-4.10.0-dwz-debuginfo.patch
# (tv) Mini debuginfo support (UPSTREAM):
Patch3502: rpm-4.10.0-minidebuginfo.patch

# Mageia patches that are easier to rediff on top of FC patches:
#---------------------------------------------------------------
# (tv) merge mga stuff from rpm-setup:
Patch4000: rpm-4.10.0-find-debuginfo__mga-cfg.diff
# (cg) fix debuginfo extraction. Sometimes, depending on local setup, the
# extraction of debuginfo can fail. This happens if you have a shared build dir
# which contains lots of subfolders for different packages (i.e. the default
# you would get if you rpm -i lots of srpms and build a whole bunch of them)
# This fix simply uses the real build dir passed in as an argument to the script
# rather than the top level %_builddir definition (aka $RPM_BUILD_DIR).
# (cg) This messes up the debuginfo packages themselves due to bad paths.
# I suspect the real problem lies in the debugedit binary which I will debug further.
# Leaving this here so I don't forget (aka it annoys tv enough to bug me if it's
# still here after any reasonable length of time!)
#Patch4007: rpm-4.11.1-fix-debuginfo-extraction.patch
# (lm) Don't uselessly bytecompile .py in docdir
Patch4008: rpm-4.11.1-dont-bytecompile-python-in-docdir.patch

Patch4009: rpm-4.11.2-double-separator-warning.patch
# (tv) make old suggests be equivalent to recommends:
Patch4010: rpm-4.12.0-oldsuggest_equals_recommends.patch
Patch4012: rpm-mga-suggests.diff

# Upstream: fix regression:
Patch4011: rpm-4.12.0-fix-missing-rpmlib-requires.patch


License:	GPLv2+
BuildRequires:	autoconf
BuildRequires:	zlib-devel
BuildRequires:  bzip2-devel
BuildRequires:	liblzma-devel >= 5
BuildRequires:	automake
BuildRequires:	elfutils-devel
BuildRequires:	libbeecrypt-devel
BuildRequires:	ed
BuildRequires:	gettext-devel
BuildRequires:  libsqlite3-devel
BuildRequires:  db5.3-devel
BuildRequires:  neon-devel
BuildRequires:	popt-devel
BuildRequires:	nss-devel
BuildRequires:	magic-devel
BuildRequires:  rpm-%{_real_vendor}-setup-build %{?rpmsetup_version:>= %{rpmsetup_version}}
BuildRequires:  readline-devel
BuildRequires:	ncurses-devel
BuildRequires:  openssl-devel
BuildRequires:  lua5.2-devel >= 5.2.3-3.mga5
BuildRequires:  libcap-devel
BuildRequires:  pkgconfig(libarchive)
# Needed for doc
#BuildRequires:	graphviz
BuildRequires:	tetex
%if %buildpython
BuildRequires:	python-devel
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

%description build
This package contains scripts and executable programs that are used to
build packages using RPM.

%package sign
Summary: Package signing support
Group:   System/Base

%description sign
This package contains support for digitally signing RPM packages.

%if %buildpython
%package -n python-rpm
Summary:	Python bindings for apps which will manipulate RPM packages
Group:		Development/Python
Requires:	rpm = %epoch:%{version}-%{release}

%description -n python-rpm
The rpm-python package contains a module which permits applications
written in the Python programming language to use the interface
supplied by RPM (RPM Package Manager) libraries.

This package should be installed if you want to develop Python
programs that will manipulate RPM packages and databases.
%endif

%prep
%setup -q -n %name-%srcver
%apply_patches

%build
aclocal
automake-1.14 --add-missing
automake
autoreconf

%if %builddebug
RPM_OPT_FLAGS=-g
%endif
export CPPFLAGS="$CPPFLAGS `pkg-config --cflags nss`"
CFLAGS="$RPM_OPT_FLAGS -fPIC" CXXFLAGS="$RPM_OPT_FLAGS -fPIC" \
    %configure2_5x \
        --enable-nls \
        --enable-python \
        --enable-sqlite3 \
        --without-javaglue \
%if %builddebug
        --enable-debug \
%endif
        --with-external-db \
%if %buildpython
        --with-python=%{pyver} \
%else
        --without-python \
%endif
%if ! %buildplugins
        --disable-plugins \
%endif
        --with-glob \
        --without-selinux \
        --without-apidocs \
        --with-cap

%make

%install
make DESTDIR=%buildroot install

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

mkdir -p %buildroot%_sysconfdir/rpm/macros.d
cat > %buildroot%_sysconfdir/rpm/macros <<EOF
# Put your own system macros here
# usually contains 

# Set this one according your locales
# %%_install_langs

EOF

%{rpmdir}/%{_host_vendor}/find-lang.pl $RPM_BUILD_ROOT %{name}

%check
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

%dir %{_localstatedir}/spool/repackage
%dir %{rpmdir}
%dir /etc/rpm
%config(noreplace) /etc/rpm/macros
%dir /etc/rpm/macros.d
%attr(0755, rpm, rpm) %{rpmdir}/config.guess
%attr(0755, rpm, rpm) %{rpmdir}/config.sub
%attr(0755, rpm, rpm) %{rpmdir}/rpmdb_*
%attr(0644, rpm, rpm) %{rpmdir}/macros
%attr(0755, rpm, rpm) %{rpmdir}/mkinstalldirs
%attr(0755, rpm, rpm) %{rpmdir}/rpm.*
%attr(0644, rpm, rpm) %{rpmdir}/rpmpopt*
%attr(0644, rpm, rpm) %{rpmdir}/rpmrc
%attr(0755, rpm, rpm) %{rpmdir}/elfdeps
%attr(0755, rpm, rpm) %{rpmdir}/script.req
%exclude %{rpmdir}/tcl.req

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
%exclude %{rpmdir}/platform/i*86-%{_os}/macros
%exclude %{rpmdir}/platform/athlon-%{_os}/macros
%exclude %{rpmdir}/platform/pentium*-%{_os}/macros
%exclude %{rpmdir}/platform/geode-%{_os}/macros
%endif
%ifarch x86_64
%attr(   -, rpm, rpm) %{rpmdir}/platform/amd64-*
%attr(   -, rpm, rpm) %{rpmdir}/platform/x86_64-*
%attr(   -, rpm, rpm) %{rpmdir}/platform/ia32e-*
%else
%exclude %{rpmdir}/platform/amd64-%{_os}/macros
%exclude %{rpmdir}/platform/ia32e-%{_os}/macros
%exclude %{rpmdir}/platform/x86_64-%{_os}/macros
%endif
%ifarch %arm
%attr(   -, rpm, rpm) %{rpmdir}/platform/arm*
%attr(   -, rpm, rpm) %{rpmdir}/platform/aarch64*/macros
%else
%exclude %{rpmdir}/platform/arm*/macros
%exclude %{rpmdir}/platform/aarch64*/macros
%endif
%ifarch %mips
%attr(   -, rpm, rpm) %{rpmdir}/platform/mips*
%endif
%attr(   -, rpm, rpm) %{rpmdir}/platform/noarch*
# new in 4.10.0:
%exclude %{rpmdir}/platform/alpha*-%{_os}/macros
%exclude %{rpmdir}/platform/sparc*-%{_os}/macros
%exclude %{rpmdir}/platform/ia64*-%{_os}/macros
%exclude %{rpmdir}/platform/m68k*-%{_os}/macros
%exclude %{rpmdir}/platform/ppc*-%{_os}/macros
%exclude %{rpmdir}/platform/s390*-%{_os}/macros
%exclude %{rpmdir}/platform/sh*-%{_os}/macros



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
%rpmattr	%{_prefix}/lib/rpm/appdata.prov
%rpmattr	%{_prefix}/lib/rpm/brp-*
%rpmattr	%{_prefix}/lib/rpm/check-files
%rpmattr	%{_prefix}/lib/rpm/debugedit
%rpmattr	%{_prefix}/lib/rpm/*.prov 
%rpmattr	%{_prefix}/lib/rpm/find-debuginfo.sh
%rpmattr	%{_prefix}/lib/rpm/find-lang.sh
%rpmattr	%{_prefix}/lib/rpm/find-provides
%rpmattr	%{_prefix}/lib/rpm/find-requires
%rpmattr	%{_prefix}/lib/rpm/perldeps.pl
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
%rpmattr	%{_prefix}/lib/rpm/osgideps.pl
%rpmattr	%{_prefix}/lib/rpm/pkgconfigdeps.sh

%rpmattr	%{_prefix}/lib/rpm/rpmdeps
%rpmattr        %{_prefix}/lib/rpm/pythondeps.sh


%{_mandir}/man8/rpmbuild.8*
%{_mandir}/man8/rpmdeps.8*

%if %buildpython
%files -n python-rpm
%{_libdir}/python*/site-packages/rpm
%endif

%files -n %librpmname
%{_libdir}/librpm.so.%{libmajor}*
%{_libdir}/librpmio.so.%{libmajor}*
%if %buildplugins
%{_libdir}/rpm-plugins
%endif

%files -n %librpmbuild
%{_libdir}/librpmbuild.so.%{libmajor}*

%files -n %librpmsign
%{_libdir}/librpmsign.so.%{libmajor}*

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

