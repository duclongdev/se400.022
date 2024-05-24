from ansi2html import Ansi2HTMLConverter
conv = Ansi2HTMLConverter()
# ansi = "".join(sys.stdin.readlines())
ansi = '[Nest] 28 - \x1b[33m<time>\x1b[0m LOG [UserAppLeaveResolver] [api - registerLeave - Mutation] [SUCCESS] request: {"leaveType":"LATE","startDate":"2024-02-02 01:31:00","endDate":"2024-02-02 06:00:59","leaveReason":"i have private business would like take off that morning","userId":"cc741b20-f392-4a2e-e00f-f418bb12be12","device":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"} \x1b[33m<processed_time>\x1b[0m [0.21 MB] \x1b[33m<elapsed_time>\x1b[0m'
html = conv.convert(ansi, False)

print(html)