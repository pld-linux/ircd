#
# Conditional build:
# _with_hm	- with soper/hawkmod patch, but without hoop3.
# _without_ipv6	- without ipv6 support.
#
Summary:	Internet Relay Chat Server
Summary(pl):	Serwer IRC (Internet Relay Chat)
Name:		ircd
Version:	2.10.3p3
Release:	3
License:	GPL
Group:		Daemons
Source0:	ftp://ftp.irc.org/irc/server/irc%{version}.tgz
# Source0-md5:	bec7916f39043609c528afac507a2e00
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Source3:	%{name}.logrotate
Patch0:		%{name}-config.patch
Patch1:		%{name}-linux.patch
Patch2:		%{name}-hm.patch
# Orginal: http://jv.irc.cz/hoop3.diff - modified because we have
# MAX_CONNECTIONS already redefined in ircd-config.patch.
# Also MIN_CHANOP_SERV, MIN_CHANOP_CHAN, MIN_CHANOP_USR to 0.
Patch3:		%{name}-hoop3.diff
URL:		http://www.irc.org/
#BuildRequires:	autoconf
BuildRequires:	ncurses-devel
BuildRequires:	textutils
BuildRequires:	zlib-devel
Prereq:		rc-scripts
Requires(pre):	/usr/bin/getgid
Requires(pre):	/bin/id
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires(post):	fileutils
Requires(post,preun):	/sbin/chkconfig
Requires(postun):	/usr/sbin/userdel
Requires(postun):	/usr/sbin/groupdel
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)
Obsoletes:	ircd-hybrid

%define		_sysconfdir	/etc/%{name}
%define		_localstatedir	/var/lib/%{name}

%description
Ircd is the server (daemon) program for the Internet Relay Chat
Program. This version supports IPv6, too.

%description -l pl
Ircd jest serwerem us�ugi IRC (Internet Relay Chat Program). Ta wersja
wspiera tak�e protok� IPv6.

%prep
%setup -q -n irc%{version}
%patch0 -p1
%patch1 -p1
%{?_with_hm:%patch2 -p1}
%{?!_with_hm:%patch3 -p1}

%build
#cd support
#	autoheader
#	autoconf
#cd ..

%configure2_13 \
	--logdir=%{_var}/log/%{name} \
	--enable-dsm \
	--with-zlib \
%{?!_without_ipv6:--enable-ip6}

cd "`support/config.guess`"
%{__make} all

%install
rm -rf $RPM_BUILD_ROOT

cd "`support/config.guess`"
install -d $RPM_BUILD_ROOT%{_var}/log/ircd
install -d $RPM_BUILD_ROOT%{_libdir}/ircd
install -d $RPM_BUILD_ROOT%{_sbindir}
install -d $RPM_BUILD_ROOT%{_mandir}/man{1,3,5,8}
install -d $RPM_BUILD_ROOT{%{_sysconfdir},/etc/{rc.d/init.d,sysconfig,logrotate.d}}
install -d $RPM_BUILD_ROOT%{_localstatedir}

%{__make} install DESTDIR=$RPM_BUILD_ROOT \
	     client_man_dir=$RPM_BUILD_ROOT%{_mandir}/man1 \
	     conf_man_dir=$RPM_BUILD_ROOT%{_mandir}/man5 \
	     server_man_dir=$RPM_BUILD_ROOT%{_mandir}/man8

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/%{name}
install %{SOURCE3} $RPM_BUILD_ROOT/etc/logrotate.d/%{name}

%{?!_without_ipv6:tr ':' '%' < $RPM_BUILD_ROOT%{_sysconfdir}/example.conf > $RPM_BUILD_ROOT%{_sysconfdir}/ircd.conf}
%{?_without_ipv6:install $RPM_BUILD_ROOT%{_sysconfdir}/example.conf $RPM_BUILD_ROOT%{_sysconfdir}/ircd.conf}

rm -f $RPM_BUILD_ROOT%{_sysconfdir}/example.conf

cat << EOF > $RPM_BUILD_ROOT%{_sysconfdir}/ircd.motd

Powered by PLD Linux Distribution IRC Server with IPv6 support!

IRC:    irc.pld.org.pl irc6.pld.org.pl
WWW:        http://www.pld.org.pl/
FTP:        ftp://ftp.pld.org.pl/
e-mail:      feedback@pld-linux.org

EOF

mv -f $RPM_BUILD_ROOT%{_bindir}/irc $RPM_BUILD_ROOT%{_bindir}/ircs
mv -f $RPM_BUILD_ROOT%{_mandir}/man1/irc.1 $RPM_BUILD_ROOT%{_mandir}/man1/ircs.1

touch $RPM_BUILD_ROOT%{_localstatedir}/ircd.{pid,tune}

%clean
rm -rf $RPM_BUILD_ROOT

%pre
if [ -n "`getgid ircd`" ]; then
	if [ "`getgid ircd`" != "75" ]; then
		echo "Error: group ircd doesn't have gid=75. Correct this before installing ircd." 1>&2
		exit 1
	fi
else
	%{_sbindir}/groupadd -f -g 75 ircd 2> /dev/null
fi
if [ -n "`id -u ircd 2>/dev/null`" ]; then
	if [ "`id -u ircd`" != "75" ]; then
		echo "Error: user ircd doesn't have uid=75. Correct this before installing ircd." 1>&2
		exit 1
	fi
else
	%{_sbindir}/useradd -g ircd -d /etc/%{name} -u 75 -s /bin/true -c "IRC Service account" ircd 2> /dev/null
fi

%post
/sbin/chkconfig --add ircd
if [ -f /var/lock/subsys/ircd ]; then
	/etc/rc.d/init.d/ircd restart 1>&2
else
	echo "Run \"/etc/rc.d/init.d/ircd start\" to start IRC daemon."
fi
touch /var/log/ircd/{auth,opers,rejects,users,ircd.log}
chmod 640 /var/log/ircd/*
chown ircd.ircd /var/log/ircd/*

%preun
# If package is being erased for the last time.
if [ "$1" = "0" ]; then
	if [ -f /var/lock/subsys/ircd ]; then
		/etc/rc.d/init.d/ircd stop 1>&2
	fi
	/sbin/chkconfig --del ircd
fi

%postun
# If package is being erased for the last time.
if [ "$1" = "0" ]; then
	%{_sbindir}/userdel ircd 2> /dev/null
	%{_sbindir}/groupdel ircd 2> /dev/null
fi

%files
%defattr(644,root,root,755)
%doc doc/{2.10-New,2.9-New,Authors,ChangeLog,Etiquette,SERVICE.txt,m4macros}
%doc doc/{example.conf,rfc*.txt,README,RELEASE_{LOG,NOTES}}
%attr(755,root,root) %{_bindir}/*
%attr(755,root,root) %{_sbindir}/*
%attr(770,root,ircd) %dir %{_var}/log/ircd
%attr(770,root,ircd) %dir %{_localstatedir}
%attr(640,ircd,ircd) %ghost %{_localstatedir}/ircd.pid
%attr(640,ircd,ircd) %ghost %{_localstatedir}/ircd.tune
%attr(750,root,ircd) %dir %{_sysconfdir}
%attr(660,root,ircd) %config(noreplace) %{_sysconfdir}/ircd.conf
%attr(660,root,ircd) %config(noreplace) %{_sysconfdir}/iauth.conf
%attr(664,root,ircd) %{_sysconfdir}/ircd.m4
%attr(664,root,ircd) %{_sysconfdir}/ircd.motd
%{_mandir}/man*/*
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%attr(644,root,root) /etc/sysconfig/%{name}
