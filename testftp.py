import ftplib
import os
import time
import paramiko
import threading

new_version = "7705-TiMOS-6.2.R8"
hosts = [
    {'address' :"x.x.x.x",'user':'xxxx','passwd':'xxxx' },
    ##{'address' :"x.x.x.x",'user':'xxxx','passwd':'xxxx' },
]

#THE METHOD WHICH IS TRIGGER THE OTHER PROCESSES(FTP Connection,FTP Upload,SSH Connection,SSH Upgrade)
def main_method(address,user,passwd):

    FTPSession = ftp_connection(address, user, passwd)
    print("\n[***]FTP Uploading Processes Starting... for: "+address+"[***]\n")
    print("\n----------------------ATTENTION: This process can take a long time.Please wait...----------------------\n")
    ftp_uploadfile(FTPSession)

    SSHSession = ssh_connection(address,user,passwd)
    print("[***]SSH Upgrading Processes Starting... for: " + address + "[***]\n")
    ssh_upgrade(SSHSession)


    SSHSession.close()
    FTPSession.close()

#SSH CONNECTION METHOD
def ssh_connection(address,user,passwd):
    print("\n[***]SSH Working for... : "+address+"[***]")
    while True:
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(address, username=user, password=passwd, port=22)
            print("[***]SSH Connection OK! on: " + address + "[***]")
            break

        except paramiko.SSHException as e:
            print("SSH error for: "+address+" Please check details: ",e)
            ssh.close()
            print("\n[***]SSH was end... on: "+address+" Type:FAILED[***]\n")
            break

    return ssh

#SSH UPGRADE METHOD
def ssh_upgrade(ssh):
    channel = ssh.invoke_shell()

    out = channel.recv(9999)
    print(out.decode("ascii"))

    channel.send('show bof | match image\n')
    channel.send('\n')
    channel.send('environment no more\n')
    out = channel.recv(9999)
    print(out.decode("ascii"))
    channel.send('\n')
    while not channel.recv_ready():
        time.sleep(0)

    out = channel.recv(9999)
    print(out.decode("ascii"))
    channel.send('show card a detail | match Free\n')
    channel.send('show card b detail | match Free\n')
    channel.send('\n')
    channel.send('file dir images/7705-TiMOS-6.2.R8\n')
    channel.send('\n')
    while not channel.recv_ready():
        time.sleep(0.1)

    out = channel.recv(9999)
    print(out.decode("ascii"))
    channel.send('file cf3:\images/7705-TiMOS-6.2.R8\ # copy boot.ldr cf3:/boot.ldr\n')
    channel.send('\n')
    print(out.decode("ascii"))
    while not channel.recv_ready():
        time.sleep(0.2)

    out = channel.recv(9999)
    print(out.decode("ascii"))
    channel.send('exit\n')
    channel.send('\n')
    channel.send('file version check cf3:/boot.ldr\n')
    channel.send('\n')
    print(out.decode("ascii"))
    while not channel.recv_ready():
        time.sleep(5)

    out = channel.recv(9999)
    print(out.decode("ascii"))
    channel.send('bof primary-image cf3:/images/7705-TiMOS-6.2.R8/ \n')
    channel.send('\n')
    channel.send('bof save\n')
    channel.send('\n')
    print(out.decode("ascii"))
    while not channel.recv_ready():
        time.sleep(8)

    out = channel.recv(9999)
    print(out.decode("ascii"))
    channel.send('admin redundancy synchronize config\n')
    channel.send('\n')
    channel.send('admin redundancy synchronize boot-env\n')
    channel.send('\n')
    while not channel.recv_ready():
        time.sleep(10)

    out = channel.recv(9999)
    print(out.decode("ascii"))
    channel.send('show redundancy synchronization\n')
    # channel.send('show redundancy synchronization | match Status\n')
    channel.send('\n')
    channel.send('file version check cf3:/boot.ldr\n')
    channel.send('\n')
    channel.send('file version check cf3:/both.tim\n')

    while not channel.recv_ready():
        time.sleep(14)

    out = channel.recv(9999)
    print(out.decode("ascii"))
    channel.send('admin save\n')
    channel.send('\n')
    channel.send('file type cf3:bof.cfg\n')

    while not channel.recv_ready():
        time.sleep(16)

    out = channel.recv(9999)
    print(out.decode("ascii"))
    channel.send('admin reboot upgrade now \n')
    channel.send('\n')
    channel.send('show boot-messages\n')
    channel.send('\n')

    while not channel.recv_ready():
        time.sleep(20)

    out = channel.recv(9999)
    print(out.decode("ascii"))

    ssh.close()

    print("\n[***]SSH was end... Type:SUCCESSFUL[***]\n")


#FTP connection Method
def ftp_connection(address,user,passwd):
    print("[***]FTP Working... for: " + address + " [***]")
    while True:

        try:
                ftp = ftplib.FTP(address)
                ftp.login(user=user, passwd=passwd)
                print(ftp.getwelcome())
                print("\n[***]FTP Connection OK! on: " + address + "[***]")
                break

        except ftplib.all_errors as e:
                print("Failed to connect to: "+address+" Check your address and credentials.Details..:", e)
                ftp.close()
                break
    return ftp

#FTP Upload Method
def ftp_uploadfile(ftp):

    while True:

        try:
                ftp.cwd("\images")
                ftp.mkd("" + new_version)
                ftp.cwd("/" + new_version)
                ftp.dir()
                file = open("boot.ldr", "rb")
                ftp.storbinary("STOR boot.ldr",file)
                file_2 = open("both.tim", "rb")
                ftp.storbinary("STOR both.tim",file_2)
                print("END!!!!!!!!!!!!!!!!!!!!!")
                ftp.dir()
                file.close()
                file_2.close()
                print("\n[***]UPLOADING OK!!! [***]")
                print("[***]FTP was end... Type:SUCCESSFUL...[***]\n")
                break

        except ftplib.all_errors as e:
                print("Failed to uploading...Please check details.Details..:", e)
                ftp.close()
                print("\n[***]FTP was end... Type:FAILED[***]")
                break

print("[***]WELCOME TO... NOKIA UPGRADE SCRIPT!!![***]")
print("[***]PROCESS STARTED...[***]\n")

threads = []
for item in hosts:
    t = threading.Thread(name='main_method', target=main_method, args=(item['address'], item['user'], item['passwd'],))
    threads.append(t)
    t.start()

for thread in threads:
    thread.join()


print("\n[***]DONE..!Everything OK..!Good bye..![***]")
