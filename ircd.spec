Name:		ircd
Version:	2.10.3
Release:	3
Copyright:	GPL
Summary:	Internet Relay Chat Server
Summary(pl):	Serwer IRC (Internet Relay Chat)
Group:		Daemons
Group(pl):	Serwery
URL:		http://www.xs4all.nl/~carlo17/ircd-dev/
Source0:	ftp://ftp.funet.fi/pub/unix/irc/server/irc%{version}.tgz
Source1:	ircd.init
Patch0:		%{name}-config.patch
Patch1:		%{name}-linux.patch
BuildPrereq:    zlib-devel
BuildPrereq:	ncurses-devel
BuildPrereq:	textutils
Requires:	rc-scripts
Prereq:		/sbin/chkconfig
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)
Obsoletes:	ircd6

%description
Ircd is the server (daemon) program for the Internet Relay
Chat Program. This version supports IPv6, too.

%description -l pl
Ircd jest serwerem us³ugi IRC (Internet Relay Chat Program).
Ta wersja wspiera tak¿e protokó³ IPv6.

%prep
%setup -q -n irc%{version}
%patch0 -p1
%patch1 -p1

%build
cd support && autoheader && autoconf && cd ..
CFLAGS="$RPM_OPT_FLAGS" LDFLAGS="-s" \
./configure \
	--prefix=%{_prefix} \
	--sbindir=%{_sbindir} \
	--logdir=%{_var}/log/%{name} \
	--sysconfdir=/etc/%{name} \
	--localstatedir=%{_var}/run \
	--with-zlib \
	--enable-ip6 \
	--enable-dsm \
        %{_target_platform}

cd `support/config.guess`
make all

%install
rm -rf $RPM_BUILD_ROOT

cd `support/config.guess`
install -d		$RPM_BUILD_ROOT%{_var}/log/ircd
install -d		$RPM_BUILD_ROOT%{_libdir}/ircd
install -d		$RPM_BUILD_ROOT%{_sbindir}
install -d		$RPM_BUILD_ROOT%{_mandir}/man{1,3,5,8}
install -d		$RPM_BUILD_ROOT/etc/{ircd,rc.d/init.d}

make install DESTDIR=$RPM_BUILD_ROOT \
	     client_man_dir=$RPM_BUILD_ROOT%{_mandir}/man1 \
	     conf_man_dir=$RPM_BUILD_ROOT%{_mandir}/man5 \
	     server_man_dir=$RPM_BUILD_ROOT%{_mandir}/man8

install %{SOURCE1}	$RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
tr ':' '%' <		$RPM_BUILD_ROOT/etc/%{name}/example.conf > \
	   		$RPM_BUILD_ROOT/etc/%{name}/ircd.conf
rm -f			$RPM_BUILD_ROOT/etc/%{name}/example.conf

cat << EOF > $RPM_BUILD_ROOT/etc/%{name}/ircd.motd

Powered by Polish Linux Distibution IRC Server with IPv6 support!

WwW:        http://www.pld.org.pl/	http://www.ipv6.pld.org.pl/
FTP:        ftp://ftp.pld.org.pl/
EMail:       pld-list@pld.org.pl

EOF

mv		$RPM_BUILD_ROOT%{_bindir}/irc		$RPM_BUILD_ROOT%{_bindir}/ircs
mv		$RPM_BUILD_ROOT%{_mandir}/man1/irc.1	$RPM_BUILD_ROOT%{_mandir}/man1/ircs.1
gzip -9nf	$RPM_BUILD_ROOT%{_mandir}/man*/* ../doc/*   || :
strip		$RPM_BUILD_ROOT{%{_bindir}/*,%{_sbindir}/*} || :

touch		$RPM_BUILD_ROOT%{_var}/run/ircd.pid

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%{_sbindir}/groupadd -f -g 75 ircd 2> /dev/null
%{_sbindir}/useradd -g ircd -d /etc/%{name} -u 75 -s /bin/true ircd 2> /dev/null

%post
/sbin/chkconfig --add ircd

%preun
# If package is being erased for the last time.
if [ $1 = 0 ]; then
	/sbin/chkconfig --del ircd
fi

%postun
# If package is being erased for the last time.
if [ $1 = 0 ]; then
	%{_sbindir}/userdel ircd 2> /dev/null
	%{_sbindir}/groupdel ircd 2> /dev/null
fi

%files
%defattr(644,root,root)
%doc doc/{2.10-New,2.9-New,Authors,ChangeLog,Etiquette,INSTALL.txt,SERVICE.txt,m4macros}.gz
%attr(755,root,root) %{_bindir}/*
%attr(755,root,root) %{_sbindir}/*
%attr(750,root,ircd) %dir /etc/%{name}
%attr(644,root,ircd) /etc/%{name}/ircd.motd
%attr(750,ircd,ircd) %dir %{_var}/log/ircd
%attr(644,ircd,ircd) %dir %{_var}/run/ircd.pid
%attr(644,root,root) %{_mandir}/man[158]/*
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%attr(644,root,root) /etc/%{name}/ircd.m4
%attr(640,root,ircd) %config(noreplace) /etc/%{name}/ircd.conf
%attr(640,root,ircd) %config(noreplace) /etc/%{name}/iauth.conf
