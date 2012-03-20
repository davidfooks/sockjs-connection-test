from ws4py.client.threadedclient import WebSocketClient
from threading import Thread, Event
from multiprocessing import Process, Queue
from time import sleep
import uuid

def main():
    logging = False
    msg_interval = 0.3
    num_tests = 50

    if logging:
        def log(message):
            print(message)
    else:
        def log(message):
            pass

    class WebSocketMessageThread(Thread):
        def __init__(self, web_socket):
            Thread.__init__(self)
            self.web_socket = web_socket

        def run(self):
            while True:
                sleep(msg_interval)
                if self.web_socket.client_terminated:
                    break
                log('Sending message')
                self.web_socket.send(u'"Hello world"')

    class TestClient(WebSocketClient):
        def __init__(self, url):
            WebSocketClient.__init__(self, url)
            self.message_thread = WebSocketMessageThread(self)

        def opened(self):
            self.message_thread.start()
            log("Connection opened")

        def closed(self, code, reason):
            log("Connection closed %d %s" % (code, reason))
            self.message_thread.join()

        def received_message(self, m):
            log("=> %d %s" % (len(m), str(m)))

    # the connection hangs once it is made so connect in a thread
    class WebSocketConnectionThread(Thread):
        def __init__(self, web_socket):
            Thread.__init__(self)
            self.web_socket = web_socket

        def run(self):
            self.web_socket.connect()

    class TestUser(Process):
        def __init__(self, queue):
            Process.__init__(self, args=(queue,))
            self.queue = queue

        def run(self):
            base_url = 'ws://127.0.0.1:9999/echo'
            trans_url = base_url + '/000/' + str(uuid.uuid4()) + '/websocket'

            ws = TestClient(trans_url)

            connect_thread = WebSocketConnectionThread(ws)
            connect_thread.start()

            while self.queue.get() != 'stop':
                pass

            ws.close()
            connect_thread.join()

    test_process_queue = [None] * num_tests
    test_process = [None] * num_tests
    for i in xrange(num_tests):
        test_process_queue[i] = Queue()
        test_process[i] = TestUser(test_process_queue[i])
        test_process[i].start()

    raw_input('Press enter to stop test...\n')

    for i in xrange(num_tests):
        test_process_queue[i].put('stop')

    for i in xrange(num_tests):
        test_process[i].join()

if __name__ == '__main__':
    main()
