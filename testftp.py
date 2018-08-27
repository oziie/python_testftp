import ftplib
import os
import time
import paramiko

address = "172.29.11.43"
user = "admin"
passwd = "gnegpec"


def ssh_connection():
    print("\n[***]SSH working...[***]")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(address, username=user, password=passwd, port=22)
    channel = ssh.invoke_shell()

    print("[***]SSH Connection OK!...[***]")

    out = channel.recv(9999)
    print(out.decode("ascii"))

    channel.send('show bof | match image\n')

    while not channel.recv_ready():
        time.sleep(0)

    out = channel.recv(9999)
    print(out.decode("ascii"))

    channel.send('file cd cf3:\images\n')
    channel.send('file\n')
    channel.send('md ftppython\n')

    print(out.decode("ascii"))

    while not channel.recv_ready():
        time.sleep(3)

    out = channel.recv(9999)
    print(out.decode("ascii"))


    print("\n[***]SSH was end...[***]")

#FTP connection method


def ftp_connection():
    print("[***]FTP working...[***]\n")

    while True:

        try:
            ##with ftplib.FTP('172.29.11.43') as ftp:
                ftp = ftplib.FTP(address)
                ftp.login(user=user, passwd=passwd)
                print(ftp.getwelcome())
                print("\n[***]FTP Connection OK![***]\n")
                print("[***]Current directory", ftp.pwd())
                ftp.cwd("\images")
                #ftp.dir()
                ## SEND FILE OR DIRECTORY
                file = r"deneme.txt"
                ftp.storbinary("STOR " + os.path.basename(file), open(file, "rb"))
                print('\n[***]Current directory', ftp.pwd())
                ftp.dir()
                print("\n[***]UPLOADING OK!!![***]",)
                print("[***]STARTING UPGRADE...[***]")



                ##ftp_command = "show bof"
                ssh_connection()

                ftp.dir()

                break
        except ftplib.all_errors as e:
                print("Failed to connect,check your address and credentials.Details..:", e)






print("[***]WELCOME TO... NOKIA UPGRADE SCRIPT!!![***]")

ftp_connection()

print("[***]Good bye...[***]")
