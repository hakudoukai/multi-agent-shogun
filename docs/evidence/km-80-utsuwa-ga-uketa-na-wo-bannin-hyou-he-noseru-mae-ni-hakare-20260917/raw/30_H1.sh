ASW_PROCESS_TIMEOUT=${ASW_PROCESS_TIMEOUT:-1}
if [ "${ASW_PROCESS_TIMEOUT:-1}" = "1" ]; then
  printf "BRANCH=timeout_process\n"
else
  printf "BRANCH=event_only\n"
fi
[ "${ASW_PROCESS_TIMEOUT:-1}" = "1" ]; printf "TEST_RC=%s\n" "$?"
printf "VALUE=[%s]\n" "${ASW_PROCESS_TIMEOUT-<unset>}"
