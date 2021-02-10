from super_serial import SuperSerial
import cmd


class SerialShell(cmd.Cmd):
    intro = "Welcome to the Serial Shell. Type help or ? to list commands.\n"
    prompt = "(serial) > "
    file = None

    def __init__(self, super_serial: SuperSerial) -> None:
        super().__init__()
        self.serial = super_serial

    def do_send(self, arg):
        self.serial.write(arg.encode("UTF-8"))

    def do_read(self, arg):
        m = self.serial.read()
        print("Raw: {}".format(m))

    def do_read_line(self, arg):
        m = self.serial.readline()
        print("Line: {}".format(m))

    def close(self):
        print("\nExiting...")
        self.serial.stop()


def main():
    serial = SuperSerial()
    serial.start()
    SerialShell(serial).cmdloop()


if __name__ == "__main__":
    main()
