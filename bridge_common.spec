Name: tendrl-bridge-common
Version: 0.0.1
Release: 1%{?dist}
BuildArch: noarch
Summary: Common Module for all Bridges
Source0: %{name}-%{version}.tar.gz
Group:   Applications/System
License: LGPLv2+
URL: https://github.com/Tendrl/bridge_common

BuildRequires: systemd
BuildRequires: python2-devel
BuildRequires: pytest

Requires: python-etcd
Requires: python-dateutil
Requires: python-hacking
Requires: pytest
Requires: python-pytest-cov
Requires: python-mock
Requires: python-sphinx
Requires: python-reno
Requires: python-coveralls

%description
Common python module usable by all Tendrl SDS Bridges

%prep
%setup %{name}-%{version}
# Remove the requirements file to avoid adding into
# distutils requiers_dist config
rm -rf {test-,}requirements.txt

# Remove bundled egg-info
rm -rf %{name}.egg-info

%build
%{__python} setup.py build

%install
%{__python} setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES
install -m 755 --directory $RPM_BUILD_ROOT%{_var}/log/tendrl/common
install -Dm 755 etc/tendrl/tendrl.conf.sample $RPM_BUILD_ROOT%{_datadir}/tendrl/commons/tendrl.conf
install -Dm 755 etc/tendrl/tendrl.conf.sample $RPM_BUILD_ROOT%{_sysconfdir}/tendrl.conf.sample

%check
py.test -v bridge_common/tests

%files -f INSTALLED_FILES
%dir %{_var}/log/tendrl/common
%doc README.rst
%license LICENSE
%{_datarootdir}/tendrl/commons/tendrl.conf
%{_sysconfdir}/tendrl.conf.sample

%changelog
* Mon Oct 17 2016 Timothy Asir Jeyasingh <tjeyasin@redhat.com> - 0.0.1-1
- Initial build.