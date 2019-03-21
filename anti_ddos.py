import time

# Config:

# 1 - We check ips. 0 - if we want to turn off checking ips
check_ip_switch = True
log_time = 20  # Number in seconds in which we check for number of logins
num_softban = 20  # Number of max acceptable logins for log_time seconds
threshold = 2

ip_filter_table = {}
num_ips = 0

OK = 0
SOFT_BAN = 1
NO_SPACE = 2


# FIXME
def clear_table():
    for ip in list(ip_filter_table):
        if ip_filter_table[ip][0]["STATUS"] == 1 \
          and time.time() - ip_filter_table[ip][0]["TIME"] > log_time:
            del ip_filter_table[ip]
        else:
            return 2


def check_ip(our_ip):
    global ip_filter_table
    global num_ips

    if not check_ip_switch:
        return OK, ""

    if num_ips >= threshold:
        clear_table()

    if num_ips >= threshold:
        return 2, "IP filer is overfilled. Please try again late"

    if our_ip not in ip_filter_table.keys():
        ip_filter_table[our_ip] = [{"TIME": time.time(),
                                   "NUM_LOGINS": 1, "STATUS": 0}]
        num_ips += 1
        return OK, ""

    if ip_filter_table[our_ip][0]["STATUS"] == 1:
        return SOFT_BAN, "You has been blocked for <x> minutes." \
                 "Please try again later."
        # TODO: return 1, time - где time это время бана, которое мы можем
        # увеличивать
    elif ip_filter_table[our_ip][0]["NUM_LOGINS"] + 1 > num_softban:
        ip_filter_table[our_ip][0]["STATUS"] = 1
        return SOFT_BAN, ""
    else:
        login_time = time.time()

        if login_time - ip_filter_table[our_ip][0]["TIME"] > log_time:
            ip_filter_table[our_ip][0]["TIME"] = login_time
            ip_filter_table[our_ip][0]["NUM_LOGINS"] = 1
            return OK, ""  # LEGIT
        else:
            ip_filter_table[our_ip][0]["NUM_LOGINS"] += 1
            return OK, ""  # LEGIT
