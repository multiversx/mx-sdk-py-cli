import stat

METACHAIN_ID = 4294967295
NETWORK_MONITORING_INTERVAL_IN_SECONDS = 1
# Read, write and execute by owner, read and execute by group and others
FILE_MODE_EXECUTABLE = stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH
