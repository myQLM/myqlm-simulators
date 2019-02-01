
###############################################################################
#
# qat-pylinalg product packaging
#
###############################################################################

%define name qat-pylinalg

%define version 0.0.1

# Using the .snapshot suffix helps the SVN tagging process.
# Please run <your_svn_checkout>/devtools/packaged/bin/auto_tag -m
# to get the auto_tag man file # and to understand the tagging process.

# If you don't care, then, just starts with
# Bull.1.0%{?dist}.%{?revision}snapshot
# and run 'make tag' when you want to tag.
%define release Bull.1.0%{?dist}.%{?revision}snapshot

# Warning: Bull's continuous compilation tools refuse the use of
# %release in the src_dir variable!
%define src_dir %{name}-%{version}
%define src_tarall %{src_dir}.tar.gz


# Make RPM installation relocatable
Prefix: /etc
Prefix: /usr


# Predefined variables:
# {%_mandir} => normally /usr/share/man (depends on the PDP)
# %{perl_vendorlib} => /usr/lib/perl5/vendor_perl/

%define src_conf_dir conf
%define src_bin_dir bin
%define src_lib_dir lib
%define src_doc_dir doc

%define target_conf_dir /etc/
%define target_bin_dir /usr/bin
%define target_lib_dir /usr/lib*
%define target_include_dir /usr/include
%define target_prefix  /usr/
%define target_data_dir  %{target_prefix}/share/
%define target_python_lib_dir %{python_sitearch}
%define target_man_dir %{_mandir}
%define target_share_dir /usr/share/%{name}
%define target_doc_dir /usr/share/doc/%{name}
%define target_notebook_dir /usr/share/doc/qat


# Package summary
Summary:        New product qat-pylinalg
Name:           %{name}
Version:        %{version}
Release:        %{release}
Source:         %{src_tarall}

# Perform a 'cat /usr/share/doc/rpm-*/GROUPS' to get a list of available
# groups. Note that you should be in the corresponding PDP to get the
# most accurate information!
# TODO: Specify the category your software belongs to
Group:          Development/Libraries
BuildRoot:      %{_tmppath}/%{name}-root
# Automatically filled in by PDP: it should not appear therefore!
#Packager:      Bull <help@bull.net>
Distribution:   Bull HPC

# Automatically filled in by PDP: it should not appear therefore!
#Vendor:         Bull
License:        'Bull S.A.S. proprietary : All rights reserved'
BuildArch:      x86_64
URL:            https://novahpc.frec.bull.fr

Provides:       %{name}

#Conflicts:

# Product dependencies
#Requires:       backtrace
#Requires:       net-snmp
#Requires:       python-cffi >= 0.8.6

# Packaging dependencies
BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  libtool
BuildRequires:  gcc
BuildRequires:  CUnit-devel

# For documentation generation
BuildRequires:  doxygen


# Main package description
%description
qat-pylinalg description

# Documenatation sub-package
%package doc
Summary: Documentation of the qat-pylinalg package

%description doc
Doxygen documentation of qat-pylinalg package

# Devel sub-package
%package devel
Summary: Header files providing the qat-pylinalg API
Requires: %{name}

%description devel
Header files providing the qat-pylinalg API

# Tests sub-package
%package tests
Requires: %{name}
Summary: Tests for the qat-pylinalg library

%description tests
Test for the qat-pylinalg library


###############################################################################
# Prepare the files to be compiled
%prep
#%setup -q -n %{name}
test "x$RPM_BUILD_ROOT" != "x" && rm -rf $RPM_BUILD_ROOT

%setup

%configure --disable-debug %{?checkdoc} \
    --with-tagfiles-prefix=%{src_tagfiles_prefix} \
    --with-tagfiles-suffix=%{src_tagfiles_suffix} \
    --with-htmldirs-prefix=%{target_htmldirs_prefix} \
    --with-htmldirs-suffix=%{target_htmldirs_suffix} \
    %{_python_env}

###############################################################################
# The current directory is the one main directory of the tar
# Order of upgrade is:
#%pretrans new
#%pre new
#install new
#%post new
#%preun old
#delete old
#%postun old
#%posttrans new
%build
%{__make}

%install
%{__make} install DESTDIR=$RPM_BUILD_ROOT  %{?mflags_install}
mkdir -p $RPM_BUILD_ROOT/%{target_doc_dir}
cp ChangeLog $RPM_BUILD_ROOT/%{target_doc_dir}
rm -f $RPM_BUILD_ROOT/%{target_lib_dir}/lib*.la

%post

%postun

%preun

%clean
cd /tmp
rm -rf $RPM_BUILD_ROOT/%{name}-%{version}
test "x$RPM_BUILD_ROOT" != "x" && rm -rf $RPM_BUILD_ROOT

###############################################################################
# Specify files to be placed into the package

# Main package
%files
%defattr(-,root,root)
#%{_libdir}/lib*
#%{target_bin_dir}/*

%{target_python_lib_dir}/*


# Changelog is automatically generated (see Makefile)
# The %doc macro already contain a default path (usually /usr/doc/)
# See:
# http://www.rpm.org/max-rpm/s1-rpm-inside-files-list-directives.html#S3-RPM-INSIDE-FLIST-DOC-DIRECTIVE for details
# %doc ChangeLog
# or using an explicit path:

%doc
       %{target_doc_dir}/ChangeLog


# Documentation sub-package files
%files doc
       %{target_doc_dir}/%{version}/



##################################################
# %changelog is automatically generated by 'make log' (see the Makefile)
##################### WARNING ####################
## Do not add anything after the following line!
##################################################
%changelog