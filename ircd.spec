#
# Conditional build
%bcond_with	crypt	# build with crypted passwords support
#
Summary:	Internet Relay Chat Server
Summary(pl.UTF-8):	Serwer IRC (Internet Relay Chat)
Name:		ircd
Version:	2.11.1p1
Release:	3
License:	GPL
Group:		Daemons
Source0:	ftp://ftp.irc.org/irc/server/irc%{version}.tgz
# Source0-md5:	c5a2b3097a5fbeb91b39412730b02ab5
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Source3:	%{name}.logrotate
Source4:	%{name}.conf
Source5:	%{name}.motd
Patch0:		%{name}-linux.patch
Patch1:		%{name}-conf_delimiter_4_easy_upgrade.patch
Patch2:		%{name}-config.patch
Patch3:		%{name}-crypt.patch
URL:		http://www.irc.org/
#BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	ncurses-devel
BuildRequires:	rpmbuild(macros) >= 1.268
BuildRequires:	zlib-devel
Requires(post):	fileutils
Requires(post,preun):	/sbin/chkconfig
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires:	rc-scripts
Provides:	group(ircd)
Provides:	user(ircd)
Obsoletes:	bircd
Obsoletes:	ircd-hybrid
Obsoletes:	ircd-ptlink
Conflicts:	logrotate < 3.7.4
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sysconfdir	/etc/%{name}
%define		_localstatedir	/var/lib/%{name}

%description
Ircd is the server (daemon) program for the Internet Relay Chat
Program. There is also version with IPv6 support enclosed.

%description -l pl.UTF-8
Ircd jest serwerem usługi IRC (Internet Relay Chat Program). Załączona
jest także wersja obsługująca IPv6.

%prep
%setup -q -n irc%{version}
%patch0 -p1
%patch1 -p1
%patch2 -p1
%{?with_crypt:%patch3 -p1}

%build
cp -f /usr/share/automake/config.* support
cp -f %{SOURCE5} support

mdir=$(pwd)
mkdir .ircd6
cp -a * .ircd6

cd .ircd6
# cannot regenerate, so use workaround
export ac_cv_lib_nsl_socket=no
%configure2_13 \
	--with-logdir=%{_var}/log/%{name} \
	--with-rundir=%{_var}/lib/%{name} \
	--enable-dsm \
	--with-zlib \
	--enable-ip6

cd "`support/config.guess`"
%{__make} all

cd $mdir

# cannot regenerate, so use workaround
export ac_cv_lib_nsl_socket=no
%configure2_13 \
	--with-logdir=%{_var}/log/%{name} \
	--with-rundir=%{_var}/lib/%{name} \
	--enable-dsm \
	--with-zlib

cd "`support/config.guess`"
%{__make} all

%install
rm -rf $RPM_BUILD_ROOT
tdir=$(support/config.guess)

rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_var}/log/{,archive/}ircd,%{_libdir}/ircd,%{_sbindir},%{_mandir}/man{1,3,5,8}} \
	$RPM_BUILD_ROOT{%{_sysconfdir},/etc/{rc.d/init.d,sysconfig,logrotate.d}} \
	$RPM_BUILD_ROOT%{_localstatedir}
cd $tdir

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT \
	client_man_dir=$RPM_BUILD_ROOT%{_mandir}/man1 \
	conf_man_dir=$RPM_BUILD_ROOT%{_mandir}/man5 \
	server_man_dir=$RPM_BUILD_ROOT%{_mandir}/man8

cd ..
for f in chkconf iauth ircd ircd-mkpasswd ircdwatch; do
	install .ircd6/${tdir}/${f} $RPM_BUILD_ROOT%{_sbindir}/${f}6
done

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/%{name}
install %{SOURCE3} $RPM_BUILD_ROOT/etc/logrotate.d/%{name}
install %{SOURCE4} $RPM_BUILD_ROOT%{_sysconfdir}/%{name}.conf

rm -f $RPM_BUILD_ROOT%{_sysconfdir}/{iauth,ircd}.conf.example
touch $RPM_BUILD_ROOT%{_localstatedir}/ircd.{pid,tune}

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -f -g 75 ircd
%useradd -g ircd -d /etc/%{name} -u 75 -s /bin/true -c "IRC Service account" ircd

%post
/sbin/chkconfig --add ircd
%service ircd restart "IRC daemon"
touch /var/log/ircd/ircd.{auth,opers,rejects,users,log}
chmod 640 /var/log/ircd/*
chown ircd:ircd /var/log/ircd/*

%preun
if [ "$1" = "0" ]; then
	%service ircd stop
	/sbin/chkconfig --del ircd
fi

%postun
if [ "$1" = "0" ]; then
	%userremove ircd
	%groupremove ircd
fi

%triggerpostun -- %{name} < 2.11.0
if [ -f %{_sysconfdir}/ircd.conf ]; then
	echo "Saving old configuration as %{_sysconfdir}/ircd.conf.rpmsave"
	cp -f %{_sysconfdir}/ircd.conf %{_sysconfdir}/ircd.conf.rpmsave
	echo "Adjusting configuration for ircd 2.11"
	sed -i -e '{ /^M%/s/$/%000A/; /^[iI]%/s/$/%/g; /^[oO]%/s/$/%/g; }' %{_sysconfdir}/ircd.conf

	# we have to do part of %post here to have ircd working after upgrade from 2.10.x to 2.11.x
	%service -q ircd restart
fi

%files
%defattr(644,root,root,755)
%doc doc/{2.11-New,2.10-New,2.9-New,Authors,ChangeLog,Etiquette,SERVICE.txt,m4macros}
%doc doc/{*.conf.example,rfc*.txt,README,RELEASE_{LOG,NOTES},stats.txt,ISO-3166-1}
%attr(755,root,root) %{_sbindir}/*
%attr(770,root,ircd) %dir %{_var}/log/ircd
%attr(770,root,ircd) %dir %{_var}/log/archive/ircd
%attr(770,root,ircd) %dir %{_localstatedir}
%attr(640,ircd,ircd) %ghost %{_localstatedir}/ircd.pid
%attr(640,ircd,ircd) %ghost %{_localstatedir}/ircd.tune
%attr(750,root,ircd) %dir %{_sysconfdir}
%attr(660,root,ircd) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/ircd.conf
%attr(660,root,ircd) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/iauth.conf
%attr(664,root,ircd) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/ircd.motd
%attr(664,root,ircd) %{_sysconfdir}/ircd.m4
%{_mandir}/man*/*
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/%{name}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/%{name}
