import subprocess, re
out=subprocess.check_output('netsh interface ipv4 show dns name="Ethernet"', shell=True, text=True, errors='ignore')
print(repr(out))
print('DHCP' in out.upper())
print(re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', out))
