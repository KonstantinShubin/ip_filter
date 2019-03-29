import time

# Config:

# 1 - We check ips. 0 - if we want to turn off checking ips
check_ip_switch = True
log_time = 3  # Number in seconds in which we check for number of logins
num_softban = 1  # Number of max acceptable logins for log_time seconds
threshold = 2
first_time_ban = 1800  # time is seconds (1800 = 30 minutes), should be > log_time
ban_time_coef = 1.5
max_ban_time = 21600  # time in seconds (21600 = 6 hours)

ip_filter_table = {}
num_ips = 0

OK = 0
SOFT_BAN = 1
NO_SPACE = 2


# FIXME
def clear_table():
    global num_ips
    for ip in list(ip_filter_table):
        if ip_filter_table[ip]["STATUS"] == 0 \
                and time.time() - ip_filter_table[ip]["TIME"] > log_time:
            del ip_filter_table[ip]
            num_ips -= 1


def check_ip(our_ip):
    global ip_filter_table
    global num_ips

    # TODO: Add function metrics

    current_time = time.time()

    if not check_ip_switch:
        return OK, "Website is currently disabled. "

    if num_ips >= threshold:
        clear_table()
        num_ips = len(ip_filter_table.keys())

    if num_ips >= threshold:
        return NO_SPACE, "IP filer is overfilled. Please try again late. "

    if our_ip not in ip_filter_table.keys():
        ip_filter_table[our_ip] = {"TIME": time.time(),
                                   "NUM_LOGINS": 1, "STATUS": 0, "BANNED_TIME": 0}
        num_ips += 1
        return OK, "Welcome, new user. "

    if ip_filter_table[our_ip]["STATUS"] == 1:
        if ip_filter_table[our_ip]["BANNED_TIME"] <= current_time - ip_filter_table[our_ip]["TIME"] and current_time - ip_filter_table[our_ip]["TIME"] > log_time:
            ip_filter_table[our_ip]["TIME"] = current_time
            ip_filter_table[our_ip]["NUM_LOGINS"] = 1
            ip_filter_table[our_ip]["STATUS"] = 0
            ip_filter_table[our_ip]["BANNED_TIME"] = 0
            return OK, "You are unbanned now. "
        elif ip_filter_table[our_ip]["BANNED_TIME"] > current_time - ip_filter_table[our_ip]["TIME"]:
            ip_filter_table[our_ip]["BANNED_TIME"] = ban_time_coef * (ip_filter_table[our_ip]["BANNED_TIME"] - (current_time - ip_filter_table[our_ip]["TIME"]))
            ip_filter_table[our_ip]["TIME"] = current_time
            if ip_filter_table[our_ip]["BANNED_TIME"] > max_ban_time:
                ip_filter_table[our_ip]["BANNED_TIME"] = max_ban_time
            remaining_ban_time = time.strftime("%H hours, %M minutes and %S seconds. ", time.gmtime(ip_filter_table[our_ip]["BANNED_TIME"]))
            return SOFT_BAN, f"Your ban time was increased by {ban_time_coef} and now is {remaining_ban_time}" \
                "Please try again later. "

    else:
        if current_time - ip_filter_table[our_ip]["TIME"] > log_time:
            ip_filter_table[our_ip]["NUM_LOGINS"] = 1
            ip_filter_table[our_ip]["TIME"] = current_time
            return OK, "Welcome. Haven't seen you for a while. "
        else:
            ip_filter_table[our_ip]["NUM_LOGINS"] += 1
            if ip_filter_table[our_ip]["NUM_LOGINS"] > num_softban:
                ip_filter_table[our_ip]["STATUS"] = 1
                ip_filter_table[our_ip]["TIME"] = current_time
                ip_filter_table[our_ip]["BANNED_TIME"] = first_time_ban
                remaining_ban_time = time.strftime("%H hours, %M minutes and %S seconds. ", time.gmtime(first_time_ban))
                return SOFT_BAN, f"You have been blocked for {remaining_ban_time}" \
                    f"If you return before this time ends, your remaining ban time will be multiplied by {ban_time_coef}. " \
                    "Please try again later. "
            else:
                return OK, "Hi again. "
