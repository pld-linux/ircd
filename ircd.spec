Summary:	The most widely used IRC server (on IRCnet for instance)
Name:		ircd
Version:	2.10.3p3
Release:	1
License:	GPL
Group:		Daemons
Source0:	ftp://ftp.irc.org/irc/server/irc%{version}.tgz
Source1:	%{name}.init
Source2:	irc2.10.3p1-config.h
URL:		http://www.irc.org/
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
# make everything except the client
%{__make} -C $MYARCH ircd iauth chkconf ircd-mkpasswd
%{__make} -C $MYARCH ircdwatch ircd_var_dir=%{_chroot}/run

%install
rm -rf $RPM_BUILD_ROOT
rm -rf %{buildroot}
%{__make} -C `support/config.guess` prefix=%{buildroot}%{_prefix} \
	server_man_dir=%{buildroot}%{_mandir}/man8 \
	conf_man_dir=%{buildroot}%{_mandir}/man5 \
	ircd_dir=%{buildroot}%{_chroot} \
ircd_conf_dir=%{buildroot}%{_chroot}%{_sysconfdir}/ircd \
	ircd_var_dir=%{buildroot}%{_chroot}/run \
	ircd_log_dir=%{buildroot}%{_chroot}/log \
	install-server

install -d %{buildroot}%{_chroot}/{etc,lib,usr/sbin,log,run}
# install -D -m 711 %{SOURCE3} %{buildroot}%{_sbindir}/ircd-crypter
install -D -m 755 $RPM_SOURCE_DIR/ircd.init %{buildroot}/etc/rc.d/init.d/ircd

echo 'This is a poorly installed IRC server (MOTD not edited)' \
> %{buildroot}%{_chroot}%{_sysconfdir}/ircd/ircd.motd
touch %{buildroot}%{_chroot}%{_sysconfdir}/resolv.conf
mv %{buildroot}%{_chroot}%{_sysconfdir}/ircd/example.conf \
%{buildroot}%{_chroot}%{_sysconfdir}/ircd/ircd.conf.dist
cp %{buildroot}%{_chroot}%{_sysconfdir}/ircd/ircd.conf.dist \
%{buildroot}%{_chroot}%{_sysconfdir}/ircd/ircd.conf

# Chroot-related
mv %{buildroot}%{_sbindir}/iauth %{buildroot}%{_chroot}%{_sbindir}
ln -sf ../..%{_chroot}%{_sbindir}/iauth %{buildroot}%{_sbindir}

ln -sf ..%{_chroot}%{_sysconfdir}/ircd %{buildroot}%{_sysconfdir}/ircd

# Borrowed from anonftp
cat > %{buildroot}%{_chroot}%{_sysconfdir}/passwd << EOF
root:*:0:0:::
bin:*:1:1:::
EOF

cat > %{buildroot}%{_chroot}%{_sysconfdir}/group << EOF
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

%define _chlib %{buildroot}%{_chroot}/lib

cp -fd %{_sysconfdir}/ld.so.cache %{buildroot}%{_chroot}%{_sysconfdir}
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
rm -rf %{buildroot}

%files
%defattr(644,root,root,755)
%doc doc/*
%attr(755,root,root)/etc/rc.d/init.d/ircd
%{_sysconfdir}/ircd
%{_mandir}/*/*
%attr(755,root,root) %{_sbindir}/*
%attr(750, root, root) %dir %{_chroot}
%{_chroot}/lib
%dir %{_chroot}%{_sysconfdir}
%dir %{_chroot}%{_prefix}
%{_chroot}%{_sbindir}
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
