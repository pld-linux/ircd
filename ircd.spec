#
# Conditional build
%bcond_with	crypt	# build with crypted passwords support
#
%define	_rc	b14
Summary:	Internet Relay Chat Server
Summary(pl):	Serwer IRC (Internet Relay Chat)
Name:		ircd
Version:	2.11.0
Release:	0.%{_rc}.1
License:	GPL
Group:		Daemons
Source0:	ftp://ftp.irc.org/irc/server/BETA/irc%{version}%{_rc}.tgz
# Source0-md5:	6e205149edf91288e313b7598fc0858c
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Source3:	%{name}.logrotate
Source4:	%{name}.conf
Patch0:		%{name}-linux.patch
Patch1:		%{name}-conf_delimiter_4_easy_upgrade.patch
Patch2:		%{name}-config.patch
Patch3:		%{name}-crypt.patch
Patch4:		%{name}-m_ping.patch
URL:		http://www.irc.org/
#BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	ncurses-devel
BuildRequires:	textutils
BuildRequires:	rpmbuild(macros) >= 1.159
BuildRequires:	zlib-devel
PreReq:		rc-scripts
Requires(pre):	/usr/bin/getgid
Requires(pre):	/bin/id
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires(post):	fileutils
Requires(post,preun):	/sbin/chkconfig
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Provides:	group(ircd)
Provides:	user(ircd)
Obsoletes:	bircd
Obsoletes:	ircd-hybrid
Obsoletes:	ircd-ptlink
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sysconfdir	/etc/%{name}
%define		_localstatedir	/var/lib/%{name}

%description
Ircd is the server (daemon) program for the Internet Relay Chat
Program. It has built-in IPv6 support.

%description -l pl
Ircd jest serwerem us�ugi IRC (Internet Relay Chat Program). Zawiera
wsparcie dla IPv6.

%prep
%setup -q -n irc%{version}%{_rc}
%patch0 -p1
%patch1 -p1
%patch2 -p1
%{?with_crypt:%patch3 -p1}
%patch4 -p1

%build
cp -f /usr/share/automake/config.* support

# cannot regenerate, so use workaround
export ac_cv_lib_nsl_socket=no
%configure2_13 \
        --with-logdir=%{_var}/log/%{name} \
        --enable-dsm \
        --with-zlib \
	--enable-ip6

cd "`support/config.guess`"
%{__make} all

%install
tdir=$(support/config.guess)

rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_var}/log/{,archiv/}ircd,%{_libdir}/ircd,%{_sbindir},%{_mandir}/man{1,3,5,8}} \
	$RPM_BUILD_ROOT{%{_sysconfdir},/etc/{rc.d/init.d,sysconfig,logrotate.d}} \
	$RPM_BUILD_ROOT%{_localstatedir}
cd $tdir

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT \
	client_man_dir=$RPM_BUILD_ROOT%{_mandir}/man1 \
	conf_man_dir=$RPM_BUILD_ROOT%{_mandir}/man5 \
	server_man_dir=$RPM_BUILD_ROOT%{_mandir}/man8

cd ..

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/%{name}
install %{SOURCE3} $RPM_BUILD_ROOT/etc/logrotate.d/%{name}
install %{SOURCE4} $RPM_BUILD_ROOT/etc/%{name}/%{name}.conf

rm -f $RPM_BUILD_ROOT%{_sysconfdir}/{iauth,ircd}.conf.example

cat << EOF > $RPM_BUILD_ROOT%{_sysconfdir}/ircd.motd

Powered by PLD Linux Distribution IRC Server!

WWW:        http://www.pld-linux.org/
FTP:        ftp://ftp.pld-linux.org/
e-mail:      feedback@pld-linux.org

EOF

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
	/usr/sbin/groupadd -f -g 75 ircd 2> /dev/null
fi
if [ -n "`id -u ircd 2>/dev/null`" ]; then
	if [ "`id -u ircd`" != "75" ]; then
		echo "Error: user ircd doesn't have uid=75. Correct this before installing ircd." 1>&2
		exit 1
	fi
else
	/usr/sbin/useradd -g ircd -d /etc/%{name} -u 75 -s /bin/true -c "IRC Service account" ircd 2> /dev/null
fi

%post
/sbin/chkconfig --add ircd
if [ -f /var/lock/subsys/ircd ]; then
	/etc/rc.d/init.d/ircd restart 1>&2
else
	echo "Run \"/etc/rc.d/init.d/ircd start\" to start IRC daemon."
fi
touch /var/log/ircd/ircd.{auth,opers,rejects,users,log}
chmod 640 /var/log/ircd/*
chown ircd:ircd /var/log/ircd/*

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
	%userremove ircd
	%groupremove ircd
fi

%files
%defattr(644,root,root,755)
%doc doc/{2.10-New,2.9-New,Authors,ChangeLog,Etiquette,SERVICE.txt,m4macros}
%doc doc/{*.conf.example,rfc*.txt,README,RELEASE_{LOG,NOTES}}
%attr(755,root,root) %{_sbindir}/*
%attr(770,root,ircd) %dir %{_var}/log/ircd
%attr(770,root,ircd) %dir %{_var}/log/archiv/ircd
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
%attr(640,root,root) %config(noreplace) %verify(not size mtime md5) /etc/sysconfig/%{name}
%attr(640,root,root) %config(noreplace) %verify(not size mtime md5) /etc/logrotate.d/%{name}
