import socket
from threading import Thread
import os

clients = []


# Thread to listen one particular client
class ClientListener(Thread):
    def __init__(self, name: str, sock: socket.socket):
        super().__init__(daemon=True)
        self.sock = sock
        self.name = name

    # clean up
    def _close(self):
        clients.remove(self.sock)
        self.sock.close()
        print(self.name + ' disconnected')

    def run(self):
        aborted = False
        while True:
            # try to read 1024 bytes from user
            # this is blocking call, thread will be paused here
            data = self.sock.recv(1024)
            if data:
                try:
                    header = data.decode("utf-8").split(';')
                except Exception:
                    print(data)
                    self._close()
                    return

                if header[0] == "FILE":
                    print("User sends file {} ({} bytes)".format(header[1], header[2]))

                file_size = int(header[2])

                self.sock.send(bytes([2]))  # Send HEADER OK signal

                filename, file_ext = os.path.splitext(header[1])
                target_path = 'dl/{}{}'.format(filename, file_ext)
                c = 1

                while os.path.exists(target_path):
                    target_path = 'dl/{}_copy{}{}'.format(filename, c, file_ext)
                    c += 1

                with open(target_path, 'ab') as new_file:
                    c = 0
                    while True:
                        data = self.sock.recv(1024)
                        if not data:
                            print("Transmission aborted")
                            break

                        new_file.write(data)
                        c += len(data)

                        if c >= file_size:
                            print("File transmitted")
                            break
                if aborted:
                    os.remove(target_path)
                    self._close()
                else:
                    self.sock.send(bytes([1]))  # Send OK signal

            else:
                # if we got no data – client has disconnected
                self._close()
                # finish the thread
                return


def main():
    next_name = 1

    if not os.path.exists("dl"):
        os.mkdir("dl")

    # AF_INET – IPv4, SOCK_STREAM – TCP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # reuse address; in OS address will be reserved after app closed for a while
    # so if we close and imidiatly start server again – we'll get error
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # listen to all interfaces at 8800 port
    sock.bind(('', 8800))
    sock.listen()
    while True:
        # blocking call, waiting for new client to connect
        con, addr = sock.accept()
        clients.append(con)
        name = 'u' + str(next_name)
        next_name += 1
        print(str(addr) + ' connected as ' + name)
        # start new thread to deal with client
        ClientListener(name, con).start()


if __name__ == "__main__":
    main()
