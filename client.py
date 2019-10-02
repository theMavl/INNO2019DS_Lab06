import socket
import os
import sys


def main():
    filename = sys.argv[1]
    sv = sys.argv[2]
    port = sys.argv[3]

    sock = socket.socket()
    sock.connect((sv, int(port)))

    with open(filename, "rb") as fp:
        size = os.path.getsize(filename)

        header = bytes("FILE;{};{}".format(filename, size), encoding='utf8')  # Send header
        sock.send(header)

        answer = sock.recv(1)  # Wait for OK signal

        if answer != bytes([2]):
            print("\rUnexpected error during header transmission")
            sock.close()
            return

        buff = fp.read(1024)
        c = 0
        while buff:
            sock.send(buff)
            c += 1024
            print("\rSending... ({} %)".format(int(c * 100 / size)), end='')
            buff = fp.read(1024)

        answer = sock.recv(1)  # Wait for OK signal

        if answer == bytes([1]):
            print("\rFile {} transmitted successfully".format(filename))
        else:
            print("\rUnexpected error during file transmission")

        sock.close()


if __name__ == "__main__":
    main()
