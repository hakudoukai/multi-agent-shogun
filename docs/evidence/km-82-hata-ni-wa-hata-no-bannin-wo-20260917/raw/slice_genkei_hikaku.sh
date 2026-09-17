    if [ "$rc" -eq 2 ]; then
        if [ "${ASW_PROCESS_TIMEOUT:-1}" = "1" ]; then
            process_unread "timeout" || true
        fi
    else
        process_unread "event" || true
    fi
