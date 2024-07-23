%define project_name myqlm-simulators

# Input
%{?!major:          %define major           0}
%{?!minor:          %define minor           0}
%{?!patchlevel:     %define patchlevel      0}
%{?!buildnumber:    %define buildnumber     0}
%{?!branch:         %define branch          master}

%if "%{branch}" == "rc" || "%{buildnumber}" == "0"
%{?!version:        %define version         %{major}.%{minor}.%{patchlevel}}
%else
%{?!version:        %define version         %{major}.%{minor}.%{patchlevel}.%{buildnumber}}
%endif

%{?!rpm_release:    %define rpm_release     bull.0.0}
%{?!python_major:   %define python_major    3}
%{?!python_minor:   %define python_minor    6}
%{?!packager:       %define packager        noreply@eviden.com}
%{?!run_by_jenkins: %define run_by_jenkins  0}
%{?!platform:       %define platform        linux-x86_64}
%{?!python_distrib: %define python_distrib  linux-x86_64}

# Defines
%define python_version      %{python_major}.%{python_minor}
%define python_rpm          python%{python_major}%{python_minor}
%define workspace           %{getenv:WORKSPACE}
%define project_prefix      %(echo %{project_name} | cut -d- -f1)
%define project_suffix      %(echo %{project_name} | cut -d- -f2-)

# Read location environment variables
%define target_bin_dir      /%{getenv:BIN_INSTALL_DIR}
%define target_lib_dir      /%{getenv:LIB_INSTALL_DIR}
%define target_headers_dir  /%{getenv:HEADERS_INSTALL_DIR}
%define target_thrift_dir   /%{getenv:THRIFT_INSTALL_DIR}
%define target_python_dir   /%{getenv:PYTHON_INSTALL_DIR}

%undefine __brp_mangle_shebangs

%if 0%{?srcrpm}
%undefine dist
%endif

# -------------------------------------------------------------------
#
# GLOBAL PACKAGE & SUB-PACKAGES DEFINITION
#
# -------------------------------------------------------------------
Name:           %{project_name}
Version:        %{version}
Release:        %{rpm_release}%{?dist}
Group:          Development/Libraries
Distribution:   QLM
Vendor:         Eviden
License:        Bull S.A.S. proprietary : All rights reserved
BuildArch:      noarch
URL:            https://eviden.com/solutions/advanced-computing/quantum-computing

Source:         %{project_name}-%{version}.tar.gz


# -------------------------------------------------------------------
#
# MAIN PACKAGE DEFINITION
#
# -------------------------------------------------------------------
Summary:  Quantum Application Toolset (QAT)
Provides: %{name}
AutoReq: no

%description
qat-fermion simulator. This package replaces the qat-dqs package.

# -------------------------------------------------------------------
#
# PREP
#
# -------------------------------------------------------------------
%prep
%setup -q -n %{project_name}-%{version}


# -------------------------------------------------------------------
#
# BUILD
#
# -------------------------------------------------------------------
%build
%if 0%{run_by_jenkins} == 0
QATDIR=%{_builddir}/qat
QAT_REPO_BASEDIR=%{_builddir}
RUNTIME_DIR=%{_builddir}/runtime

source /usr/local/bin/qatenv
# Restore artifacts
ARTIFACTS_DIR=$QAT_REPO_BASEDIR/artifacts
mkdir -p $RUNTIME_DIR
dependent_repos="$(get_dependencies.sh build %{project_name})"
while read -r dependent_repo; do
    [[ -n $dependent_repo ]] || continue
    tar xfz $ARTIFACTS_DIR/${dependent_repo}-*.tar.gz -C $RUNTIME_DIR
done <<< "$dependent_repos"
bldit -t debug -nd -ni -v ${name}
%endif


# -------------------------------------------------------------------
#
# INSTALL
#
# -------------------------------------------------------------------
%install
QATDIR=%{_builddir}/qat
QAT_REPO_BASEDIR=%{_builddir}
INSTALL_DIR=%{buildroot}

# Install it
%if 0%{run_by_jenkins} == 0
source /usr/local/bin/qatenv
bldit -t debug -nd -nc -nm ${name}

# Save artifact
ARTIFACTS_DIR=$QAT_REPO_BASEDIR/artifacts
mkdir -p $ARTIFACTS_DIR
tar cfz $ARTIFACTS_DIR/%{project_name}-%{version}-%{platform}-%{python_rpm}-%{python_distrib}.tar.gz -C $INSTALL_DIR .
%else
# Restore installed files
mkdir -p $INSTALL_DIR
tar xfz %{workspace}/%{project_name}-%{version}-%{platform}-%{python_rpm}-%{python_distrib}.tar.gz -C $INSTALL_DIR
%endif

rm -rf $INSTALL_DIR/usr/local/lib64/python%{python_version}/qaptiva-packages/qat/__init__.py


# -------------------------------------------------------------------
#
# FILES
#
# -------------------------------------------------------------------
# Main package
%files
%defattr(-,root,root)
%{target_python_dir}/qat/pylinalg/*
%{target_python_dir}/qat/qpus/hook_pylinalg.py
%{target_python_dir}/qat/simulated_annealing/*


# -------------------------------------------------------------------
#
# SCRIPTLETS
#
# -------------------------------------------------------------------
%pre

%post

%postun

%preun


# -------------------------------------------------------------------
#
# CHANGELOG
#
# -------------------------------------------------------------------
%changelog
* Mon Jul 22 2024 Jerome Pioux <jerome.pioux@eviden.com>
  Initial RPM for Distributed Qaptiva.
