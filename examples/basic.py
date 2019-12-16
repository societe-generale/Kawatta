import kawatta

callbacks = kawatta.HumanReadableLogsCallbacks()
kawatta.compare({1: 2, 3: 4}, {1: 3}, callbacks)
callbacks.print_log()