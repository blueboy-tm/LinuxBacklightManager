import wget
import shutil
import os
import sys

APP_VERSION = '1.0.1'

if os.geteuid() != 0:
    print("Root Access required, run as `root` user or use `sudo`.")
    sys.exit()


print('Start downloading tuxedo keyboard.')
try:
    filename = wget.download("https://github.com/tuxedocomputers/tuxedo-keyboard/archive/refs/heads/master.zip")
except Exception:
    print("Error in download! check your internet connection.")
    sys.exit()

print('\nStart unpack tuxedo keyboard.')
shutil.unpack_archive(filename)

os.remove(filename)

print('Start Compile and install tuxedo keyboard.')
os.chdir("tuxedo-keyboard-master")
os.system("make clean > /dev/null")
os.system("make > /dev/null")
os.system("make clean > /dev/null")
os.system("make dkmsinstall > /dev/null")
os.system("echo tuxedo_keyboard >> /etc/modules")
os.system('echo "options tuxedo_keyboard mode=0 color_left=0xFFFFFF color_center=0xFFFFFF color_right=0xFFFFFF" > /etc/modprobe.d/tuxedo_keyboard.conf')

os.chdir("..")
shutil.rmtree("tuxedo-keyboard-master")

print('Start install Linux Backlight Manager', APP_VERSION)
os.system("rm -rf /opt/lbm-{}".format(APP_VERSION))
os.system("mkdir /opt/lbm-{}".format(APP_VERSION))

app = os.path.join(getattr(sys, '_MEIPASS'), 'app')
icon = os.path.join(getattr(sys, '_MEIPASS'), 'icon.png')
os.system(f"mv {app} /opt/lbm-{APP_VERSION}/LinuxBacklightManager")
os.system(f"mv {icon} /opt/lbm-{APP_VERSION}/icon.png")
os.system("chmod +r /opt/lbm-{}/LinuxBacklightManager".format(APP_VERSION))
os.system("chmod +x /opt/lbm-{}/LinuxBacklightManager".format(APP_VERSION))
os.system("chmod +r /opt/lbm-{}/icon.png".format(APP_VERSION))
service = f"""[Unit]
Description=LBM {APP_VERSION}
After=systemd-user-sessions.service

[Service]
Type=simple
ExecStart=/opt/lbm-{APP_VERSION}/LinuxBacklightManager boot 
User=root

[Install]
WantedBy=multi-user.target

"""
open('/etc/systemd/system/lbm.service', 'w').write(service)

desktop = f"""[Desktop Entry]
Type=Application
Encoding=UTF-8
Name=LBM {APP_VERSION}
Comment=Linux Back light
Exec=bash -c '/opt/lbm-{APP_VERSION}/LinuxBacklightManager'
Terminal=false
Icon=/opt/lbm-{APP_VERSION}/icon.png

"""
open('/etc/xdg/autostart/lbm.desktop', 'w').write(desktop)

os.system('systemctl enable lbm.service')

print('Installing Proccess Finishd. Reboot after 3s')
os.system('sleep 3')
os.system('reboot')