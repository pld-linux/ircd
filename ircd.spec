Name:		ircd
Version:	2.10.3p1
Release:	1
License:	GPL
Summary:	Internet Relay Chat Server
Summary(pl):	Serwer IRC (Internet Relay Chat)
Group:		Daemons
Group(pl):	Serwery
URL:		http://www.xs4all.nl/~carlo17/ircd-dev/
Source0:	ftp://ftp.funet.fi/pub/unix/irc/server/irc%{version}.tgz
Source1:	%{name}.init
Patch0:		%{name}-config.patch
Patch1:		%{name}-linux.patch
Patch2:		%{name}-no_libnsl.patch
BuildPrereq:	zlib-devel
BuildPrereq:	ncurses-devel
BuildPrereq:	textutils
Requires:	rc-scripts
Prereq:		/sbin/chkconfig
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)
Obsoletes:	ircd6

%define		_sysconfdir	/etc/%{name}
%define		_localstatedir	/var/lib/%{name}

%description
Ircd is the server (daemon) program for the Internet Relay Chat
Program. This version supports IPv6, too.

%description -l pl
Ircd jest serwerem us³ugi IRC (Internet Relay Chat Program). Ta wersja
wspiera tak¿e protokó³ IPv6.

%prep
%setup -q -n irc%{version}
%patch0 -p1
%patch1 -p1
%patch2 -p1

%build
LDFLAGS="-s"
cd support && autoheader && autoconf && cd ..
%configure \
	--logdir=%{_var}/log/%{name} \
	--enable-ip6 \
	--enable-dsm

cd "`support/config.guess`"
%{__make} all

%install
rm -rf $RPM_BUILD_ROOT

cd "`support/config.guess`"
install -d $RPM_BUILD_ROOT%{_var}/log/ircd
install -d $RPM_BUILD_ROOT%{_libdir}/ircd
install -d $RPM_BUILD_ROOT%{_sbindir}
install -d $RPM_BUILD_ROOT%{_mandir}/man{1,3,5,8}
install -d $RPM_BUILD_ROOT{%{_sysconfdir}/ircd,/etc/rc.d/init.d}
install -d $RPM_BUILD_ROOT%{_localstatedir}

%{__make} install DESTDIR=$RPM_BUILD_ROOT \
	     client_man_dir=$RPM_BUILD_ROOT%{_mandir}/man1 \
	     conf_man_dir=$RPM_BUILD_ROOT%{_mandir}/man5 \
	     server_man_dir=$RPM_BUILD_ROOT%{_mandir}/man8

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}

tr ':' '%' < $RPM_BUILD_ROOT%{_sysconfdir}/example.conf > \
	$RPM_BUILD_ROOT%{_sysconfdir}/ircd.conf
rm -f $RPM_BUILD_ROOT%{_sysconfdir}/example.conf

cat << EOF > $RPM_BUILD_ROOT%{_sysconfdir}/ircd.motd

Powered by Polish Linux Distibution IRC Server with IPv6 support!

WwW:        http://www.pld.org.pl/	http://www.ipv6.pld.org.pl/
FTP:        ftp://ftp.pld.org.pl/
EMail:       pld-list@pld.org.pl

EOF

mv -f $RPM_BUILD_ROOT%{_bindir}/irc $RPM_BUILD_ROOT%{_bindir}/ircs
mv -f $RPM_BUILD_ROOT%{_mandir}/man1/irc.1 $RPM_BUILD_ROOT%{_mandir}/man1/ircs.1

gzip -9nf $RPM_BUILD_ROOT%{_mandir}/man*/* ../doc/{2.10-New,2.9-New,Authors,ChangeLog,Etiquette,SERVICE.txt,m4macros}

touch $RPM_BUILD_ROOT%{_localstatedir}/ircd.{pid,tune}

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%{_sbindir}/groupadd -f -g 75 ircd 2> /dev/null
%{_sbindir}/useradd -g ircd -d /etc/%{name} -u 75 -s /bin/true ircd 2> /dev/null

%post
/sbin/chkconfig --add ircd
if [ -f /var/lock/subsys/httpd ]; then
	/etc/rc.d/init.d/ircd restart 1>&2
else
	echo "Run \"/etc/rc.d/init.d/ircd start\" to start IRC daemon."
fi

%preun
# If package is being erased for the last time.
if [ $1 = 0 ]; then
	if [ -f /var/lock/subsys/ircd ]; then
		/etc/rc.d/init.d/ircd stop 1>&2
	fi
	/sbin/chkconfig --del ircd
fi

%postun
# If package is being erased for the last time.
if [ $1 = 0 ]; then
	%{_sbindir}/userdel ircd 2> /dev/null
	%{_sbindir}/groupdel ircd 2> /dev/null
fi

%files
%defattr(644,root,root,755)
%doc doc/*.gz
%attr(755,root,root) %{_bindir}/*
%attr(755,root,root) %{_sbindir}/*
%attr(750,ircd,ircd) %dir %{_var}/log/ircd
%attr(750,ircd,ircd) %dir %{_localstatedir}
%attr(640,ircd,ircd) %ghost %{_localstatedir}/ircd.pid
%attr(640,ircd,ircd) %ghost %{_localstatedir}/ircd.tune
%attr(750,root,ircd) %dir %{_sysconfdir}
%attr(640,root,ircd) %config(noreplace) %{_sysconfdir}/ircd.conf
%attr(640,root,ircd) %config(noreplace) %{_sysconfdir}/iauth.conf
%attr(644,root,ircd) %{_sysconfdir}/ircd.m4
%attr(644,root,ircd) %{_sysconfdir}/ircd.motd
%{_mandir}/man*/*
%attr(754,root,root) /etc/rc.d/init.d/%{name}
