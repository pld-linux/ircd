Summary:	The most widely used IRC server (on IRCnet for instance)
Summary(pl):	Serwer IRC (Internet Relay Chat)
Name:		ircd
Version:	2.10.3p3
Release:	1
License:	GPL
Group:		Daemons
Source0:	ftp://ftp.irc.org/irc/server/irc%{version}.tgz
Source1:	%{name}.init
Source2:	irc2.10.3p1-config.h
URL:		http://www.irc.org/
BuildRequires:	zlib-devel
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)
PreReq:		/sbin/chkconfig

# Needed so the package doesn't provide all the glibc libs!
AutoReqProv:	no
Provides:	ircd

%define _chroot /var/lib/ircd

%description
ircd is the server (daemon) program for the Internet Relay Chat
Program. The ircd is a server in that its function is to "serve" the
client program irc(1) with messages and commands. All commands and
user messages are are passed directly to the ircd for processing and
relaying to other ircd sites.

%description -l pl
Ircd jest serwerem us³ugi IRC (Internet Relay Chat Program). Ta wersja
wspiera tak¿e protokó³ IPv6.

%prep
%setup -q -n irc%version

%build
export CFLAGS="%{rpmcflags}"
./configure \
	--prefix=%{_prefix} \
	--libdir=%{_chroot} \
	--localstatedir=/run \
	--sysconfdir=%{_sysconfdir}/ircd \
	--logdir=/log \
	--mandir=%{_mandir} \
	--with-zlib \
	--enable-ip6 \
	--enable-dsm
MYARCH=`support/config.guess`
install -m 644 %{SOURCE2} $MYARCH/config.h

%{__make} -C $MYARCH ircd iauth chkconf ircd-mkpasswd
%{__make} -C $MYARCH ircdwatch ircd_var_dir=%{_chroot}/run

%install
rm -rf $RPM_BUILD_ROOT
%{__make} -C `support/config.guess` prefix=$RPM_BUILD_ROOT%{_prefix} \
	server_man_dir=$RPM_BUILD_ROOT%{_mandir}/man8 \
	conf_man_dir=$RPM_BUILD_ROOT%{_mandir}/man5 \
	ircd_dir=$RPM_BUILD_ROOT%{_chroot} \
	ircd_conf_dir=$RPM_BUILD_ROOT%{_chroot}%{_sysconfdir}/ircd \
	ircd_var_dir=$RPM_BUILD_ROOT%{_chroot}/run \
	ircd_log_dir=$RPM_BUILD_ROOT%{_chroot}/log \
	install-server

install -d $RPM_BUILD_ROOT%{_chroot}/{etc,lib,usr/sbin,log,run}
install -D -m 755 $RPM_SOURCE_DIR/ircd.init $RPM_BUILD_ROOT/etc/rc.d/init.d/ircd

cat << EOF > $RPM_BUILD_ROOT%{_chroot}%{_sysconfdir}/ircd/ircd.motd

Powered by PLD Linux Distibution IRC Server with IPv6 support!

WWW:        http://www.pld.org.pl/
FTP:        ftp://ftp.pld.org.pl/
e-mail:      feedback@pld.org.pl

EOF

touch $RPM_BUILD_ROOT%{_chroot}%{_sysconfdir}/resolv.conf
mv $RPM_BUILD_ROOT%{_chroot}%{_sysconfdir}/ircd/example.conf \
$RPM_BUILD_ROOT%{_chroot}%{_sysconfdir}/ircd/ircd.conf.dist
cp $RPM_BUILD_ROOT%{_chroot}%{_sysconfdir}/ircd/ircd.conf.dist \
$RPM_BUILD_ROOT%{_chroot}%{_sysconfdir}/ircd/ircd.conf

# Chroot-related
mv $RPM_BUILD_ROOT%{_sbindir}/iauth $RPM_BUILD_ROOT%{_chroot}%{_sbindir}
ln -sf ../..%{_chroot}%{_sbindir}/iauth $RPM_BUILD_ROOT%{_sbindir}

ln -sf ..%{_chroot}%{_sysconfdir}/ircd $RPM_BUILD_ROOT%{_sysconfdir}/ircd

# Borrowed from anonftp
cat > $RPM_BUILD_ROOT%{_chroot}%{_sysconfdir}/passwd << EOF
root:*:0:0:::
bin:*:1:1:::
EOF

cat > $RPM_BUILD_ROOT%{_chroot}%{_sysconfdir}/group << EOF
root::0:
bin::1:
daemon::2:
sys::3:
adm::4:
EOF

%define LDSOVER 2
%define LIBCVER 2.2.5
%define LIBCRYPTVER 1
%define LIBNSLVER 1
%define LIBNSSVER 2
%define LIBCSOVER 6
%define LIBDLVER 2

%define _chlib $RPM_BUILD_ROOT%{_chroot}/lib

cp -fd %{_sysconfdir}/ld.so.cache $RPM_BUILD_ROOT%{_chroot}%{_sysconfdir}
cp -fd /lib/libc.so.%{LIBCSOVER} /lib/libc-%{LIBCVER}.so	%{_chlib}
cp -fd /lib/ld-linux.so.%{LDSOVER} /lib/ld-%{LIBCVER}.so	%{_chlib}
cp -fd /lib/libcrypt-%{LIBCVER}.so \
	/lib/libcrypt.so.%{LIBCRYPTVER}				%{_chlib}
cp -fd /lib/libnsl-%{LIBCVER}.so \
	/lib/libnsl.so.%{LIBNSLVER}				%{_chlib}
cp -fd /lib/libnss_compat-%{LIBCVER}.so \
	/lib/libnss_compat.so.%{LIBNSSVER}			%{_chlib}
cp -fd /lib/libnss_dns-%{LIBCVER}.so \
	/lib/libnss_dns.so.%{LIBNSSVER}				%{_chlib}
cp -fd /lib/libnss_files-%{LIBCVER}.so \
	/lib/libnss_files.so.%{LIBNSSVER}			%{_chlib}
cp -fd /lib/libresolv-%{LIBCVER}.so \
	/lib/libresolv.so.%{LIBNSSVER}				%{_chlib}
cp -fd /lib/libdl-%{LIBCVER}.so \
	/lib/libdl.so.%{LIBDLVER}				%{_chlib}
# strip %{_chlib}/*


%post
/sbin/chkconfig --add ircd
# Make the resolver happy
install -m 644 /etc/resolv.conf %{_chroot}/etc
# Touch the log files
touch %{_chroot}/log/auth
touch %{_chroot}/log/opers
touch %{_chroot}/log/rejects
touch %{_chroot}/log/users
chmod 640 %{_chroot}/log/*

%preun
if [ $1 = 0 ] ; then
	/sbin/service ircd stop >/dev/null 2>&1
	rm -f /var/ircd/run/*
	/sbin/chkconfig --del ircd
fi

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc doc/*
%attr(755,root,root)/etc/rc.d/init.d/ircd
%{_sysconfdir}/ircd
%{_mandir}/*/*
%attr(750, root, root) %dir %{_chroot}
%{_chroot}/lib
%dir %{_chroot}%{_sysconfdir}
%dir %{_chroot}%{_prefix}
%{_chroot}%{_sysconfdir}/ld.so.cache
%attr(444,root,root) %config %{_chroot}%{_sysconfdir}/passwd
%attr(444,root,root) %config %{_chroot}%{_sysconfdir}/group
%ghost %{_chroot}%{_sysconfdir}/resolv.conf
%attr(750, root, root) %config %dir %{_chroot}%{_sysconfdir}/ircd
%config(noreplace) %{_chroot}%{_sysconfdir}/ircd/ircd.conf
%config %{_chroot}%{_sysconfdir}/ircd/ircd.conf.dist
%config(noreplace) %{_chroot}%{_sysconfdir}/ircd/iauth.conf
%{_chroot}%{_sysconfdir}/ircd/ircd.m4
%config(noreplace) %{_chroot}%{_sysconfdir}/ircd/ircd.motd
%dir %{_chroot}/log
%dir %{_chroot}/run
%dir %{_chroot}%{_sbindir}
%dir %{_sbindir}
%attr(755, root, root) %{_sbindir}/*
%attr(755, root, root) %{_chroot}%{_sbindir}/iauth
