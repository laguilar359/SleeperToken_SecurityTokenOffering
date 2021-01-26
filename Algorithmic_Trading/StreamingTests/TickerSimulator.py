import zmq, math, time, random

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind('tcp://127.0.0.1:5555')

class FakeTicker(object):

    def __init__(self):
        self.symbol = "SYMBOL"
        self.t = time.time()
        self.value = 100.0
        self.sigma = 0.4
        self.r = 0.01

    def simulate_value(self):
        """
         Generates a new, random stock price.
        """

        # Record Time
        t = time.time()

        # Time interval between current time and that stored
        # in self.t in trading year fractions
        dt = (t - self.t) / (252 * 8 * 60 * 60)

        # To have larger instrument price movements - arbitrary
        dt *= 500

        self.t = t

        self.value *= math.exp((self.r - 0.5 * self.sigma ** 2) * dt +
                                self.sigma * math.sqrt(dt) * random.gauss(0,1))

        return self.value

ft = FakeTicker()

while True:
    msg = "{} {:.2f}".format(ft.symbol, ft.simulate_value())
    print(msg)

    #MSG sent to subscribed sockets
    socket.send_string(msg)
    time.sleep(random.random() *2)