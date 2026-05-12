#!/usr/bin/env bash
# Render ProxySQL libconfig from APRP env vars, then exec proxysql.
# The configuration is regenerated when credentials change so new passwords
# take effect without manual edits inside the container.

set -euo pipefail

datadir="${PROXYSQL_DATADIR:-/var/lib/proxysql}"
fp_file="${datadir}/.aprp_proxy_creds_fp"
db_file="${datadir}/proxysql.db"

mkdir -p "${datadir}"

: "${DB_USER:?DB_USER is required}"
: "${DB_PASSWORD:?DB_PASSWORD is required}"
: "${DB_ROOT_PASSWORD:?DB_ROOT_PASSWORD is required}"
: "${PROXYSQL_ADMIN_USER:?PROXYSQL_ADMIN_USER is required}"
: "${PROXYSQL_ADMIN_PASSWORD:?PROXYSQL_ADMIN_PASSWORD is required}"

db_user="${DB_USER}"
db_password="${DB_PASSWORD}"
db_root_password="${DB_ROOT_PASSWORD}"
admin_user="${PROXYSQL_ADMIN_USER}"
admin_password="${PROXYSQL_ADMIN_PASSWORD}"

primary_host="${APRP_GALERA_PRIMARY_HOST:-db}"
mirror_host="${APRP_GALERA_MIRROR_HOST:-}"

export PROXYSQL_DATADIR="${datadir}"
export db_user db_password db_root_password admin_user admin_password
export primary_host mirror_host

fp="$(
  printf '%s\0' \
    "${db_user}" \
    "${db_password}" \
    "${db_root_password}" \
    "${admin_user}" \
    "${admin_password}" |
    sha256sum |
    awk '{print $1}'
)"

need_init=0
if [[ ! -f "${db_file}" ]]; then
  need_init=1
elif [[ ! -f "${fp_file}" ]]; then
  need_init=1
elif ! grep -qxF "${fp}" "${fp_file}" 2>/dev/null; then
  need_init=1
fi

if [[ "${need_init}" -eq 1 ]]; then
  rm -f "${db_file}" "${fp_file}"
  perl -CSD -w <<'PERL' || exit 1
use strict;
use warnings;

sub qstr {
  my ($value) = @_;
  return "\"\"" if !defined($value) || $value eq q{};
  my $copy = $value;
  $copy =~ s/\\/\\\\/g;
  $copy =~ s/"/\\"/g;
  $copy =~ s/\n/\\n/g;
  $copy =~ s/\r/\\r/g;
  return '"' . $copy . '"';
}

my $d = $ENV{PROXYSQL_DATADIR} // '/var/lib/proxysql';
for my $key (
  qw(db_user db_password db_root_password admin_user admin_password primary_host))
{
  die "missing env ${key}\n" if !defined $ENV{$key} || $ENV{$key} eq q{};
}
my $u = $ENV{db_user};
my $p = $ENV{db_password};
my $r = $ENV{db_root_password};
my $au = $ENV{admin_user};
my $ap = $ENV{admin_password};
my $primary = $ENV{primary_host};
my $mirror = $ENV{mirror_host} // q{};

open my $out, q{>:utf8}, q{/tmp/proxysql.cnf} or die $!;
print {$out} 'datadir=' . qstr($d) . "\n";
print {$out} 'errorlog=' . qstr("${d}/proxysql.log") . "\n";
print {$out} <<'HDR';
admin_variables=
{
HDR
print {$out} '    admin_credentials=' . qstr( $au . ':' . $ap ) . "\n";
print {$out} <<'HDR2';
    mysql_ifaces="0.0.0.0:6032"
}
mysql_variables=
{
    threads=4
    max_connections=2048
    default_query_delay=0
    default_query_timeout=36000000
    have_compress=true
    poll_timeout=2000
    interfaces="0.0.0.0:6033"
    default_schema="information_schema"
    stacksize=1048576
    server_version="10.11.6-MariaDB"
HDR2
print {$out} '    monitor_username="root"' . "\n";
print {$out} '    monitor_password=' . qstr($r) . "\n";
print {$out} <<'HDR3';
    monitor_history=600000
    monitor_connect_interval=60000
    monitor_ping_interval=10000
    monitor_read_only_interval=1500
    monitor_read_only_timeout=500
    ping_interval_server_msec=120000
    ping_timeout_server=500
    commands_stats=true
    sessions_sort=true
    connect_retries_on_failure=10
    connect_timeout_server=3000
}
mysql_galera_hostgroups=
(
    {
        writer_hostgroup=10
        backup_writer_hostgroup=11
        reader_hostgroup=12
        offline_hostgroup=9999
        max_writers=1
        writer_is_also_reader=1
        max_transactions_behind=100
        comment="aprp galera"
    }
)
mysql_servers=
(
    { address="__PRIMARY__" , port=3306 , hostgroup=10 , max_connections=200 }__MIRROR__
)
mysql_users:
(
HDR3
my $mirror_row = q{};
$primary =~ s/\\/\\\\/g;
$primary =~ s/"/\\"/g;
if ( $mirror ne q{} ) {
  $mirror =~ s/\\/\\\\/g;
  $mirror =~ s/"/\\"/g;
  $mirror_row =
    qq{,\n    { address="$mirror" , port=3306 , hostgroup=10 , max_connections=200 }};
}

print {$out} q{};  # keep formatting stable for later substitutions

  if ( $u eq 'root' ) {
    print {$out} <<'ROOTA';
    {
        username="root"
ROOTA
    print {$out} '        password=' . qstr($r) . "\n";
    print {$out} <<'ROOTB';
        default_hostgroup=10
        active=1
    }
ROOTB
  } else {
    print {$out} <<'UA';
    {
UA
    print {$out} '        username=' . qstr($u) . "\n";
    print {$out} '        password=' . qstr($p) . "\n";
    print {$out} <<'UB';
        default_hostgroup=10
        active=1
    },
    {
        username="root"
UB
    print {$out} '        password=' . qstr($r) . "\n";
    print {$out} <<'UC';
        default_hostgroup=10
        active=1
    }
UC
  }

  print {$out} <<'TAIL';
)
mysql_query_rules:
(
)
TAIL
  close $out or die $!;
PERL
  perl -pi -e 's/__PRIMARY__/'"$(
    printf '%s' "${primary_host}" | perl -pe 's/\\/\\\\/g; s/"/\\"/g;'
  )"'/g' /tmp/proxysql.cnf
  if [[ -n "${mirror_host}" ]]; then
    perl -pi -e 's/__MIRROR__/'"$(
      printf ',\n    { address="%s" , port=3306 , hostgroup=10 , max_connections=200 }' \
        "${mirror_host}" |
        perl -pe 's/\\/\\\\/g; s/"/\\"/g;'
    )"'/g' /tmp/proxysql.cnf
  else
    perl -pi -e 's/__MIRROR__//g' /tmp/proxysql.cnf
  fi
  printf '%s\n' "${fp}" >"${fp_file}"
  exec proxysql -f --idle-threads -D "${datadir}" -c /tmp/proxysql.cnf
fi

exec proxysql -f --idle-threads -D "${datadir}"
