import wget
import shutil
import os
import sys

APP_VERSION = '1.0.0-beta'

if os.geteuid() != 0:
    print("Root Access required, run as `root` user or use `sudo`.")
    sys.exit()


print('Start downloading tuxedo keyboard.')
filename = wget.download("https://github.com/tuxedocomputers/tuxedo-keyboard/archive/refs/heads/master.zip")

print('\nStart unpack tuxedo keyboard.')
shutil.unpack_archive(filename)

os.remove(filename)

print('Start Compile and install tuxedo keyboard.')
os.chdir("tuxedo-keyboard-master")
os.system("make clean")
os.system("make")
os.system("make clean")
os.system("make dkmsinstall")
os.system("echo tuxedo_keyboard >> /etc/modules")
os.system('echo "options tuxedo_keyboard mode=0 color_left=0xFF0000 color_center=0x00FF00 color_right=0x0000FF" > /etc/modprobe.d/tuxedo_keyboard.conf')

os.chdir("..")
shutil.rmtree("tuxedo-keyboard-master")

print('Start install Linux Backlight Manager', APP_VERSION)
os.system("rm -rf /opt/lbm-{}".format(APP_VERSION))
os.system("mkdir /opt/lbm-{}".format(APP_VERSION))

app = os.path.join(getattr(sys, '_MEIPASS'), 'app')
icon = os.path.join(getattr(sys, '_MEIPASS'), 'icon.png')
os.system(f"mv {app} /opt/lbm-{APP_VERSION}/LinuxBacklightManager")
os.system(f"mv {icon} /opt/lbm-{APP_VERSION}/icon.png")
os.system("chmod -R 777 /opt/lbm-{}".format(APP_VERSION))
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