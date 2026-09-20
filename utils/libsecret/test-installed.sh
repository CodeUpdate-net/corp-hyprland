#!/bin/bash
# Exercise only a disposable container's mock service, never a personal keyring.
set -euo pipefail
[[ -e /run/.containerenv ]] || { echo 'Disposable Podman container required' >&2; exit 1; }
exec dbus-run-session bash -s <<'PRIVATE_BUS_TEST'
set -euo pipefail
python3 /usr/share/libsecret/mock-service-normal.py > /tmp/mock-service.log 2>&1 &
mock_pid=$!
trap 'kill "$mock_pid" 2>/dev/null || true' EXIT
for attempt in $(seq 1 40); do
 if [[ -s /tmp/mock-service.log ]]; then break; fi
 sleep .1
done
export SECRET_SERVICE_BUS_NAME
SECRET_SERVICE_BUS_NAME=$(head -1 /tmp/mock-service.log)
[[ $SECRET_SERVICE_BUS_NAME == :* ]]
printf '%s' 'disposable-copr-test' | secret-tool store --label='COPR libsecret test' corp-validation isolated
test "$(secret-tool lookup corp-validation isolated)" = disposable-copr-test
secret-tool clear corp-validation isolated
if secret-tool lookup corp-validation isolated; then echo 'Cleared secret still exists' >&2; exit 1; fi
echo SECRET_SERVICE_RUNTIME_PASSED

PRIVATE_BUS_TEST
