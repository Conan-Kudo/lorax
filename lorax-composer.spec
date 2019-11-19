%define debug_package %{nil}

Name:           lorax-composer
Version:        19.7.36
Release:        1%{?dist}
Summary:        Lorax Image Composer API Server

Group:          Applications/System
License:        GPLv2+
URL:            https://github.com/weldr/lorax
# To generate Source0 do:
# git clone https://github.com/weldr/lorax
# git checkout -b archive-branch lorax-%%{version}-%%{release}
# tito build --tgz
Source0:        %{name}-%{version}.tar.gz

BuildRequires: python2-devel
# For Sphinx documentation build
BuildRequires: python-sphinx yum python-mako pykickstart
BuildRequires: python-flask python-gobject libgit2-glib python2-pytoml python-semantic_version

Requires: lorax >= 19.7.22
Requires(pre): /usr/bin/getent
Requires(pre): /usr/sbin/groupadd
Requires(pre): /usr/sbin/useradd

Requires: python2-pytoml
Requires: python-semantic_version
Requires: libgit2
Requires: libgit2-glib
Requires: python-flask
Requires: python-gevent
Requires: anaconda-tui
Requires: qemu-img
Requires: tar
Requires: pykickstart >= 1.99.66.20

%{?systemd_requires}
BuildRequires: systemd

%description
lorax-composer provides a REST API for building images using lorax.

%package -n composer-cli
Summary: A command line tool for use with the lorax-composer API server

Requires: python-urllib3

%description -n composer-cli
A command line tool for use with the lorax-composer API server. Examine recipes,
build images, etc. from the command line.

%prep
%setup -q

%build
make docs

%install
rm -rf $RPM_BUILD_ROOT
make DESTDIR=$RPM_BUILD_ROOT mandir=%{_mandir} install

# Install example blueprints from the test suite.
# This path MUST match the lorax-composer.service blueprint path.
mkdir -p $RPM_BUILD_ROOT/var/lib/lorax/composer/blueprints/
for bp in example-http-server.toml example-development.toml example-atlas.toml; do
    cp ./tests/pylorax/blueprints/$bp $RPM_BUILD_ROOT/var/lib/lorax/composer/blueprints/
done

# Do Not Package the lorax files
rm -f $RPM_BUILD_ROOT/%{python_sitelib}/lorax-*.egg-info
rm -rf $RPM_BUILD_ROOT/%{python_sitelib}/pylorax/*py
rm -rf $RPM_BUILD_ROOT/%{python_sitelib}/pylorax/*py?
rm -rf $RPM_BUILD_ROOT/%{_datadir}/lorax/appliance
rm -rf $RPM_BUILD_ROOT/%{_datadir}/lorax/config_files
rm -rf $RPM_BUILD_ROOT/%{_datadir}/lorax/live
rm -rf $RPM_BUILD_ROOT/%{_datadir}/lorax/pxe-live
rm -rf $RPM_BUILD_ROOT/%{_mandir}/man1/*
rm -f $RPM_BUILD_ROOT/%{_datadir}/lorax/*tmpl
rm -f $RPM_BUILD_ROOT/%{_sbindir}/lorax
rm -f $RPM_BUILD_ROOT/%{_sbindir}/livemedia-creator
rm -f $RPM_BUILD_ROOT/%{_sbindir}/mkefiboot
rm -f $RPM_BUILD_ROOT/%{_bindir}/image-minimizer
rm -f $RPM_BUILD_ROOT/%{_bindir}/mk-s390-cdboot
rm -f $RPM_BUILD_ROOT/%{_sysconfdir}/lorax/lorax.conf

%pre
getent group weldr >/dev/null 2>&1 || groupadd -r weldr >/dev/null 2>&1 || :
getent passwd weldr >/dev/null 2>&1 || useradd -r -g weldr -d / -s /sbin/nologin -c "User for lorax-composer" weldr >/dev/null 2>&1 || :

%post
%systemd_post lorax-composer.service
%systemd_post lorax-composer.socket

%preun
%systemd_preun lorax-composer.service
%systemd_preun lorax-composer.socket

%postun
%systemd_postun_with_restart lorax-composer.service
%systemd_postun_with_restart lorax-composer.socket

%files
%defattr(-,root,root,-)
%doc COPYING AUTHORS
%doc docs/html
%dir %{_sysconfdir}/lorax/
%config(noreplace) %{_sysconfdir}/lorax/composer.conf
%{python_sitelib}/pylorax/api/*
%dir %{_datadir}/lorax/composer
%{_datadir}/lorax/composer/*
%{_sbindir}/lorax-composer
%{_unitdir}/lorax-composer.service
%{_unitdir}/lorax-composer.socket
%{_tmpfilesdir}/lorax-composer.conf
%dir %attr(0771, root, weldr) %{_sharedstatedir}/lorax/composer/
%dir %attr(0771, root, weldr) %{_sharedstatedir}/lorax/composer/blueprints/
%attr(0771, weldr, weldr) %{_sharedstatedir}/lorax/composer/blueprints/*

%files -n composer-cli
%{_bindir}/composer-cli
%{python_sitelib}/composer/*
%{_sysconfdir}/bash_completion.d/composer-cli

%changelog
* Tue Nov 19 2019 Brian C. Lane <bcl@redhat.com> 19.7.36-1
- tests: restart composer after adding optional reporsitory (atodorov)
  Related: rhbz#1770193
- tests: Keep beakerlib repo on the VM for tests which need it (atodorov)
  Related: rhbz#1770193
- tests: unskip Qcow2 scenario (atodorov)
  Related: rhbz#1770193
- tests: Ensure failure if beakerlib results file not found (atodorov)
  Related: rhbz#1770193
- tests: Documentation updates (atodorov)
  Related: rhbz#1770193
- tests: Use host repositories for make vm (atodorov)
  Related: rhbz#1770193
  Remove unused make targets (atodorov)
  Related: rhbz#1770193
- DRY when setting up, running & parsing results for beakerlib tests (atodorov)
  Related: rhbz#1770193
- tests: Fix check_root_account when used with tar liveimg test (bcl)
  Related: rhbz#1770193
- tests: Use the same asserts as before (atodorov)
  Related: rhbz#1770193
- tests: switch to using podman instead of docker (atodorov)
  Related: rhbz#1770193
- tests: Remove nested vm from tar liveimg kickstart test (bcl)
  Related: rhbz#1770193
- tests: Use --http0.9 for curl ssh test (bcl)
  Related: rhbz#1770193
- test: Boot the live-iso faster, and login using ssh key (bcl)
  Related: rhbz#1770193
- tests: Split testing the image into a separate script (bcl)
  Related: rhbz#1770193
- test: Split up the test class to allow booting other images (bcl)
  Related: rhbz#1770193
- [tests] Collect compose logs after each build (atodorov)
  Related: rhbz#1770193
- [tests] Use a function to wait for compose to finish (jikortus)
  Related: rhbz#1770193
- [tests] Use functions for starting and stopping lorax-composer (atodorov)
  Related: rhbz#1770193
- Update for differences from py3 in the backported code (bcl)
  Related: rhbz#1718473
- Remove repos.git related tests (bcl)
  Related: rhbz#1718473
- composer-cli: Update diff support for customizations and repos.git (bcl)
  Related: rhbz#1718473
- Add support for customizations and repos.git to /blueprints/diff/ (bcl)
  Related: rhbz#1718473
- tests: Update custom-base with customizations (bcl)
  Related: rhbz#1718473
- Change customizations.firewall to append items instead of replace (bcl)
  Related: rhbz#1718473
- Update customizations.services documentation (bcl)
  Related: rhbz#1718473
- lorax-composer: Add services support to blueprints (bcl)
  Related: rhbz#1718473
- lorax-composer: Add firewall support to blueprints (bcl)
  Related: rhbz#1718473
- lorax-composer: Add locale support to blueprints (bcl)
  Related: rhbz#1718473
- Update docs for new timezone section (bcl)
  Related: rhbz#1718473
- lorax-composer: Add timezone support to blueprint (bcl)
  Related: rhbz#1718473
- Proposal for adding to the blueprint customizations (bcl)
  Related: rhbz#1718473
- tests: Document Azure setup (atodorov)
- tests: unskip Azure scenario (atodorov)
- Support CI testing against a bots project PR (martin)
- Makefile: Update bots target for moved GitHub project (sanne.raymaekers)
- tests: Add kickstart tar installation test (jikortus)
  Related: rhbz#1733504
- tests: Increase test VM memory to 3 GB (jikortus)
  Related: rhbz#1733504
- tests: add option to disable kernel command line parameters check (jikortus)
  Related: rhbz#1733504
- tests: Use a loop to wait for VM and sshd to start (bcl)
  Related: rhbz#1733504
- tests: Drop sort from compose types test (bcl)
  Related: rhbz#1749802
- New test: assert toml files in git workspace (atodorov)
  Related: rhbz#1749802
- Change paths for '/api/status' calls and skip this test (atodorov)
  Related: rhbz#1698366
- Ignore Cockpit CI files when linting (atodorov)
  Related: rhbz#1698366
- Use optional repository in Live ISO test (atodorov)
  Related: rhbz#1698366
- Install test dependencies inside virtualenv (atodorov)
  Related: rhbz#1698366
- Install python2-pip in the test VM and disable EPEL repo (atodorov)
  Related: rhbz#1698366
- Use qemu-kvm in tests instead of qemu-system (atodorov)
  Related: rhbz#1698366
- Skip AWS, Azure, qcow2 and live-iso tests (atodorov)
  Related: rhbz#1698366
- Don't hard-code the path to toml-compare (atodorov)
  Related: rhbz#1698366
- Install or remove packages in the test environment (atodorov)
  Related: rhbz#1698366
- Install additional repositories for testing (atodorov)
  Related: rhbz#1698366
- Prevent ssh asking for password when testing on interactive terminal (atodorov)
  Related: rhbz#1704209
- Fail if number of excuted tests != number of dicovered tests (atodorov)
  Related: rhbz#1698366
- Fix typo from test backport (atodorov)
  Related: rhbz#1698366
- Use passwd --status for locked root account check (jikortus)
  Related: rhbz#1687595
- Backport changes for Cockpit CI (atodorov)
  Related: rhbz#1698366
* Mon Jun 24 2019 Brian C. Lane <bcl@redhat.com> 19.7.35-1
- test_compose_tar: Fix docker test (lars)
  Related: rhbz#1720224
- tests: kill the qemu process name used to start it (bcl)
  Related: rhbz#1710877
- Update local copy of lorax to current rhel7-branch (bcl)
  Related: rhbz#1668520
  Related: rhbz#1715116
  Related: rhbz#1689314
- Update the lorax templates to match what lorax provides (bcl)
  Related: rhbz#1689314
- Enable networking in lorax-composer templates (bcl)
  Resolves: rhbz#1710877

* Thu Jun 13 2019 Brian C. Lane <bcl@redhat.com> 19.7.34-1
- [tests] Handle blueprints in setup_tests/teardown_tests correctly (atodorov)
  Related: rhbz#1698366
- tests: Set BLUEPRINTS_DIR in all cases (lars)
  Related: rhbz#1698366
- tests: Change the way how we remove pyOpenSSL (atodorov)
  Related: rhbz#1715003
- Use a less strict regex for disabled root account check (jikortus)
  Related: rhbz#1687595
- Add test for passing custom option on kernel command line (jikortus)
  Related: rhbz#1688335
- Use verify_image function as a helper for generic tests (jikortus)
  Related: rhbz#1704209

* Tue May 07 2019 Brian C. Lane <bcl@redhat.com> 19.7.33-1
- Pass ssl certificate options to anaconda (lars)
  Resolves: rhbz#1701033
- Change [[modules]] to [[packages]] in tests (atodorov)
  Related: rhbz#1698366
- Add new test to verify compose paths exist (atodorov)
  Related: rhbz#1698366
- Add new sanity tests for blueprints (atodorov)
  Related: rhbz#1698366

* Mon Apr 29 2019 Brian C. Lane <bcl@redhat.com> 19.7.32-1
- tests: Add a test for using [[customizations]] with [customizations.kernel] (bcl)
  Related: rhbz#1688335
- lorax-composer: Fix customizations when creating a recipe (bcl)
  Related: rhbz#1688335

* Mon Apr 29 2019 Brian C. Lane <bcl@redhat.com> 19.7.31-1
- Fixup print function usage with StringIO (bcl)
  Related: rhbz#1688335
- lorax-composer: pass customization.kernel append to extra_boot_args (bcl)
  Resolves: rhbz#1688335
- lorax-composer: Add the ability to append to the kernel command-line (bcl)
  Related: rhbz#1688335

* Wed Apr 24 2019 Brian C. Lane <bcl@redhat.com> 19.7.30-1
- Add test for starting compose with deleted blueprint (jikortus)
  Related: rhbz#1683442
- lorax-composer: Return UnknownBlueprint errors when using deleted blueprints (bcl)
  Resolves: rhbz#1683442
- lorax-composer: Delete workspace copy when deleting blueprint (bcl)
  Related: rhbz#1683442
- Use existing storage account (jstodola)
  Related: rhbz#1673012
- Record date/time of VM creation (jstodola)
  Related: rhbz#1673012
- Update datastore for VMware testing (chrobert)
  Related: rhbz#1656105
- Fixes for locked root account test (jikortus)
  Related: rhbz#1687595
- Add checks for disabled root account (jikortus)
  Related: rhbz#1687595
- 'compose info' is 'compose details' on RHEL-7 (jikortus)
  Related: rhbz#1687595
- Update some grammer issues in the test Bash scripts (chrobert)
  Related: rhbz#1656105
- Update datastore for VMware testing (chrobert)
  Related: rhbz#1656105

* Tue Mar 19 2019 Brian C. Lane <bcl@redhat.com> 19.7.29-1
- Allow overriding $CLI outside test scripts (atodorov)
  Related: rhbz#1687595
- Use make ci inside test-in-copy target (atodorov)
  Related: rhbz#1687595
- New test: Build live-iso and boot with KVM (atodorov)
  Related: rhbz#1656105
- New test: Build qcow2 compose and test it with QEMU-KVM (atodorov)
  Related: rhbz#1656105
- New test: Verify tar images with Docker and systemd-nspawn (atodorov)
  Related: rhbz#1656105
- Update OpenStack flavor and network settings in tests (atodorov)
  Related: rhbz#1656105
- Install ansible and openstacksdk inside virtualenv (atodorov)
  Related: rhbz#1656105
- Remove python-requests, python-dateutil and pyOpenSSL (atodorov)
  Related: rhbz#1656105
- Add /usr/local/bin to PATH for tests (atodorov) (atodorov)
- Do not generate journal.xml from beakerlib (atodorov)
  Related: rhbz#1656105
- Expand parameters as separate words (jstodola) (jstodola)

* Mon Feb 25 2019 Brian C. Lane <bcl@redhat.com> 19.7.28-1
- lorax-composer: Check for STATUS before deleting (bcl)
  Related: rhbz#1659129
- Check for existing CANCEL request, and exit on FINISHED (bcl)
  Related: rhbz#1659129
- Add cancel_func to virt and novirt_install functions (bcl)
  Resolves: rhbz#1659129
- Remove duplicate repositories from the sources list (bcl)
  Resolves: rhbz#1664128
- Remove unneeded else from for/else loop. It confuses pylint (bcl)
  Related: rhbz#1666517
- Allow customizations to be specified as a toml list (dshea)
  Resolves: rhbz#1666517
- Make sure compose build tests run with SELinux in enforcing mode (jikortus)
  Related: rhbz#1654795
- Add tests for metapackages and package name globs (bcl)
  Related: rhbz#1641601
- Upgrade pip & setuptools b/c they are rather old (atodorov) (atodorov)
- Workaround openstacksdk dependency issue (atodorov) (atodorov)
- On Python 2 Azure needs the futures module (atodorov) (atodorov)
- On RHEL 7 we have Python 2, not Python 3 (atodorov) (atodorov)
- On RHEL 7 we have yum instead of dnf (atodorov) (atodorov)
- On RHEL 7 `compose info` is `compose details` (atodorov) (atodorov)
- Report an error if the blueprint doesn't exist (bcl) (bcl)
- Build the HTML docs before running tests (atodorov) (atodorov)
- Disable pylint errors with Flask and gevent (bcl) (bcl)
- Backport cloud image tests from master (atodorov) (atodorov)
- Fix compose_args for openstack image (bcl)
  Related: rhbz#1656105
- Fix compose_args for vmdk image (bcl)
  Related: rhbz#1656105
- Fix compose_args for vhd image (bcl)
  Related: rhbz#1656105
- Fix compose_args for ami image (bcl)
  Related: rhbz#1656105
- Update projects list to return only the unique projects (bcl)
  Related: rhbz#1657055
- Change yaps_to_module to proj_to_module (bcl)
  Related: rhbz#1657055
- lorax-composer: Handle packages with multiple builds (bcl)
  Resolves: rhbz#1657055
- lorax-composer: Check the queue and results at startup (bcl)
  Resolves: rhbz#1657054
- Add an openstack image type (bcl)
  Resolves: rhbz#1656105
- Replace /etc/machine-id with an empty file (dshea)
  Related: rhbz#1656105
- Add virt guest agents to the qcow2 compose (dshea)
  Resolves: rhbz#1656105
- Add a vmdk compose type. (dshea)
  Resolves: rhbz#1656105
- Add a vhd compose type for Azure images (dshea)
  Resolves: rhbz#1656105
- Add an ami compose type for AWS images (dshea)
  Resolves: rhbz#1656105
- Remove --fstype from the generated part line (dshea)
  Related: rhbz#1656105
- lorax-composer: Install selinux-policy-targeted in images (bcl)
  Resolves: rhbz#1654795
- Remove setfiles from mkrootfsimage (bcl)
  Resolves: rhbz#1654795
- Remove SELinux Permissive checks (bcl)
  Resolves: rhbz#1654795

* Mon Oct 22 2018 Brian C. Lane <bcl@redhat.com> 19.7.27-1
- Use matchPackageNames instead of searchNames (bcl)
  Resolves: rhbz#1641601

* Mon Oct 08 2018 Brian C. Lane <bcl@redhat.com> 19.7.26-1
- Revert "Rename composer-cli to composer" (bcl)
  Related: rhbz#1635760

* Fri Oct 05 2018 Brian C. Lane <bcl@redhat.com> 19.7.25-1
- Rename composer-cli to composer (lars)
  Resolves: rhbz#1635760

* Mon Oct 01 2018 Brian C. Lane <bcl@redhat.com> 19.7.24-1
- Add a test for repo metadata expiration (bcl)
  Related: rhbz#1632962
- Create a new YumBase object when repodata changes (bcl)
  Resolves: rhbz#1632962
- Fix projects_depsolve_with_size version globbing (bcl)
  Resolves: rhbz#1628114
- Add a version glob test forprojects_depsolve_with_size (bcl)
  Resolves: rhbz#1628114
- Add tests for setting root password and ssh key with blueprints (bcl)
  Related: rhbz#1626120
- Use rootpw for setting the root password instead of user (bcl)
  Related: rhbz#1626120
- Lock the root account, except on live-iso (bcl)
  Resolves: rhbz#1626120

* Wed Sep 19 2018 Brian C. Lane <bcl@redhat.com> 19.7.23-1
- Fix depsolve version globbing (bcl)
  Resolves: rhbz#1628114
- Fix /compose/cancel API documentation (bcl)

* Mon Aug 27 2018 Brian C. Lane <bcl@redhat.com> 19.7.22-1
- Fix composer-cli blueprints changes to get correct total (bcl)
- Fix blueprints/list and blueprints/changes to return the correct total (bcl)
- Add tests for limit=0 routes (bcl)
- Add a function to get_url_json_unlimited to retrieve the total (bcl)
- Fix tests related to blueprint name changes (bcl)
- Add 'example' to the example blueprint names (bcl)
- Don't include glusterfs.toml as an example blueprint (bcl)
- Add a pylorax.api.version number (bcl)
- composer-cli should not log to a file by default (bcl)
- Add documentation for using a DVD as the package source (bcl)
- Set TCP listen backlog for API socket to SOMAXCONN (lars)
- Add a note about using lorax-composer.service (bcl)
- In composer-cli, request all results (dshea)
- Fix bash_completion.d typo (bcl)
- Fix a little bug in running "modules list". (clumens)
- Add tests for /compose/status filter arguments (dshea)
- Allow '*' as a uuid in /compose/status/<uuid> (dshea)
- Add filter arguments to /compose/status (dshea)

* Thu Aug 09 2018 Brian C. Lane <bcl@redhat.com> 19.7.21-1
- Move disklabel and UEFI support to compose.py (bcl)
- Fix more tests. (clumens)
- Change INVALID_NAME to INVALID_CHARS. (clumens)
- Update composer-cli for the new error return types. (clumens)
- Add default error IDs everywhere else. (clumens)
- Add error IDs to things that can go wrong when running a compose. (clumens)
- Add error IDs for common source-related errors. (clumens)
- Add error IDs for unknown modules and unknown projects. (clumens)
- Add error IDs for when an unknown commit is requested. (clumens)
- Add error IDs for when an unknown blueprint is requested. (clumens)
- Add error IDs for when an unknown build UUID is requested. (clumens)
- Add error IDs for bad state conditions. (clumens)
- Change the error return type for bad limit= and offset=. (clumens)
- Don't sort error messages. (clumens)
- Fix bash completion of compose info (bcl)
- Add + to the allowed API string character set (bcl)
- Add job_* timestamp support to compose status (bcl)
- Add a test for the pylorax.api.timestamp functions (bcl)
- Add etc/bash_completion.d/composer-cli (wwoods)
- composer-cli: clean up "list" commands (wwoods)
- Add input string checks to the branch and format arguments (bcl)
- Add a test for invalid characters in the API route (bcl)
- Return a JSON error instead of a 404 on certain malformed URLs. (clumens)
- Return an error if /modules/info doesn't return anything. (clumens)
- Update documentation (clumens).
  Resolves: rhbz#409
- Use constants instead of strings (clumens).
  Resolves: rhbz#409
- Write timestamps when important events happen during the compose (clumens).
  Resolves: rhbz#409
- Return multiple timestamps in API results (clumens).
  Resolves: rhbz#409
- Add a new timestamp.py file to the API directory (clumens).
  Resolves: rhbz#409
- Run as root/weldr by default. (clumens)
- Use the first enabled system repo for the test (bcl)
- Show more details when the system repo delete test fails (bcl)
- Add composer-cli function tests (bcl)
- Add a test library (bcl)
- composer-cli: Add support for Group to blueprints diff (bcl)
- Adjust the tests so they will pass on CentOS7 and RHEL7 (bcl)
- Update status.py to use new handle_api_result (bcl)
- Update sources.py to use new handle_api_result (bcl)
- Update projects.py to use new handle_api_result (bcl)
- Update modules.py to use new handle_api_result (bcl)
- Update compose.py to use new handle_api_result (bcl)
- Update blueprints.py to use new handle_api_result (bcl)
- Modify handle_api_result so it can be used in more places (bcl)
- composer-cli: Fix non-zero epoch in projets info (bcl)
- Fix help output on the compose subcommand. (clumens)
- Add timestamps to "compose-cli compose status" output. (clumens)
- And then add real output to the status command. (clumens)
- Add the beginnings of a new status subcommand. (clumens)

* Fri Jul 20 2018 Brian C. Lane <bcl@redhat.com> 19.7.20-1
- Document that you shouldn't run lorax-composer twice. (clumens)
- Add PIDFile to the .service file. (clumens)
- Log and exit on metadata update errors at startup (bcl)
- Check /projects responses for null values. (bcl)
- Clarify error message from /source/new (bcl)
- Download metadata when updating or adding new repos (bcl)

* Fri Jul 13 2018 Brian C. Lane <bcl@redhat.com> 19.7.19-1
- Support loading groups from the kickstart template files. (clumens)
- Add group-based tests. (clumens)
- Include groups in depsolving. (clumens)
- Add support for groups to blueprints. (clumens)
- Check the compose templates at startup (bcl)
- List individual package install failures (bcl)
- lorax-composer: Update documentation (bcl)
- Add help output to each subcommand. (clumens)
- Split the help output into its own module. (clumens)
- If the help subcommand is given, print the help output. (clumens)

* Wed Jun 27 2018 Brian C. Lane <bcl@redhat.com> 19.7.18-1
- Only include some of the test blueprints (bcl)
- Include example blueprints in the rpm (bcl)
- Make sure /run/weldr has correct ownership and permissions (bcl)

* Wed Jun 20 2018 Brian C. Lane <bcl@redhat.com> 19.7.17-1
- new lorax-composer package built with tito

* Tue Jun 19 2018 Brian C. Lane <bcl@redhat.com> - 19.7.16-2
- New lorax-composer only package
