import threading
import subprocess
import random
import signal
import platform


class NARS:
    def __init__(self, nars_type):  # nars_type: 'opennars' or 'ONA'
        self.inference_cycle_frequency = 1  # set too large will get delayed and slow down the game
        self.operation_left = False
        self.operation_right = False
        self.operation_fire = False
        self.type = nars_type
        self.launch_nars()
        self.launch_thread()

    def launch_nars(self):
        if platform.system() == "Windows":
            shell_cmd = ["cmd"]
        else:
            shell_cmd = ["/bin/bash"]

        self.process = subprocess.Popen(shell_cmd, bufsize=1,
                                        stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE,
                                        universal_newlines=True,  # convert bytes to text/string
                                        shell=False)
        if self.type == 'opennars':
            self.add_to_cmd('java -Xmx1024m -jar opennars.jar')  # self.add_to_cmd('java -Xmx2048m -jar opennars.jar')
        elif self.type == 'ONA':
            self.add_to_cmd('NAR shell')
        self.add_to_cmd('*volume=0')

    def launch_thread(self):
        self.read_line_thread = threading.Thread(target=self.read_line,
                                                 args=(self.process.stdout,))
        self.read_line_thread.daemon = True  # thread dies with the exit of the program
        self.read_line_thread.start()

    def read_line(self, out):
        pass

    def process_kill(self):
        self.process.send_signal(signal.CTRL_C_EVENT)
        self.process.terminate()

    def babble(self):
        pass

    def add_to_cmd(self, str):
        self.process.stdin.write(str + '\n')
        self.process.stdin.flush()

    def add_inference_cycles(self, num):
        self.process.stdin.write(f'{num}\n')
        self.process.stdin.flush()

    def update(self, hero, enemy_group):  # update sensors (object positions), remind goals, and make inference
        self.update_sensors(hero, enemy_group)
        self.remind_goal()
        self.add_inference_cycles(self.inference_cycle_frequency)

    def update_sensors(self, hero, enemy_group):
        enemy_left = False
        enemy_right = False
        enemy_ahead = False
        for enemy in enemy_group.sprites():
            if enemy.rect.right < hero.rect.centerx:
                enemy_left = True
            elif hero.rect.centerx < enemy.rect.left:
                enemy_right = True
            else:  # enemy.rect.left <= hero.rect.centerx and hero.rect.centerx <= enemy.rect.right
                enemy_ahead = True
        if enemy_left:
            self.add_to_cmd('<{enemy} --> [left]>. :|:')
        if enemy_right:
            self.add_to_cmd('<{enemy} --> [right]>. :|:')
        if enemy_ahead:
            self.add_to_cmd('<{enemy} --> [ahead]>. :|:')

    def move_left(self):  # NARS gives <(*,{SELF}) --> ^left>. :|:
        self.operation_left = True
        self.operation_right = False
        print('move left')

    def move_right(self):  # NARS gives <(*,{SELF}) --> ^right>. :|:
        self.operation_left = False
        self.operation_right = True
        print('move right')

    def dont_move(self):  # NARS gives <(*,{SELF}) --> ^deactivate>. :|:
        self.operation_left = False
        self.operation_right = False
        print('stay still')

    def fire(self):  # NARS gives <(*,{SELF}) --> ^strike>. :|:
        self.operation_fire = True
        print('fire')

    def remind_goal(self):
        self.add_to_cmd('<{SELF} --> [good]>! :|:')

    def praise(self):
        self.add_to_cmd('<{SELF} --> [good]>. :|:')

    def punish(self):
        self.add_to_cmd('(--,<{SELF} --> [good]>). :|:')
        # self.add_to_cmd('<{SELF} --> [good]>. :|: %0%')  # opennars' grammar
        # self.add_to_cmd('<{SELF} --> [good]>. :|: {0}')  # ONA's grammar


class opennars(NARS):
    def __init__(self):
        super().__init__('opennars')
        self.inference_cycle_frequency = 5

    def babble(self):
        rand_int = random.randint(1, 7)
        if rand_int == 1:
            self.move_left()
            self.add_to_cmd('<(*,{SELF}) --> ^left>. :|:')
        if rand_int == 2:
            self.move_right()
            self.add_to_cmd('<(*,{SELF}) --> ^right>. :|:')
        if rand_int == 3:
            self.dont_move()
            self.add_to_cmd('<(*,{SELF}) --> ^deactivate>. :|:')
        else:
            self.fire()
            self.add_to_cmd('<(*,{SELF}) --> ^strike>. :|:')

    def read_line(self, out):  # read line without blocking
        for line in iter(out.readline, b'\n'):  # get operations
            if line[0:3] == 'EXE':
                subline = line.split(' ', 2)[2]
                operation = subline.split('(', 1)[0]
                if operation == '^left':
                    self.move_left()
                elif operation == '^right':
                    self.move_right()
                elif operation == '^deactivate':
                    self.dont_move()
                elif operation == '^strike':
                    self.fire()
        out.close()


class ONA(NARS):
    def __init__(self):
        super().__init__('ONA')
        self.inference_cycle_frequency = 0

    def read_line(self, out):  # read line without blocking
        for line in iter(out.readline, b'\n'):  # get operations
            if (line[0] == '^'):
                operation = line.split(' ', 1)[0]
                if operation == '^left':
                    self.move_left()
                elif operation == '^right':
                    self.move_right()
                elif operation == '^deactivate':
                    self.dont_move()
                elif operation == '^fire':
                    self.fire()
        out.close()
