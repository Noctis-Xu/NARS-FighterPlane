import threading
import subprocess
import random
import psutil


class NARS:
    def __init__(self, nars_type):  # nars_type: 'opennars' or 'ONA'
        self.inference_cycle_frequency = 1  # set too large will get delayed and slow down the game
        self.operation_left = False
        self.operation_right = False
        self.type = nars_type
        self.launch_nars()
        self.launch_thread()

    def launch_nars(self):
        if self.type == 'opennars':
            command = ['java', '-Xmx1024m', '-jar', 'opennars.jar']
        elif self.type == 'ONA':
            command = ['NAR.exe', 'shell']
        else:
            command = ['java', '-Xmx1024m', '-jar', 'opennars.jar']

        self.process = subprocess.Popen(command, bufsize=1,
                                        stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        universal_newlines=True,  # convert bytes to text/string
                                        shell=False)
        self.add_to_cmd('*volume=0')

    def launch_thread(self):
        self.read_line_thread = threading.Thread(target=self.read_line,
                                                 args=(self.process.stdout,))
        self.read_line_thread.daemon = True  # thread dies with the exit of the program
        self.read_line_thread.start()

    def read_line(self, out):
        pass

    def process_kill(self):
        if self.process and self.process.poll() is None:
            try:
                parent = psutil.Process(self.process.pid)
                for child in parent.children(recursive=True):
                    child.kill()
                parent.kill()
                print("[process_kill] Process tree killed.")
            except Exception as e:
                print(f"[process_kill] Failed: {e}")

    def babble(self):
        pass

    def add_to_cmd(self, str):
        if self.process and self.process.stdin:
            self.process.stdin.write(str + '\n')
            self.process.stdin.flush()
        else:
            print("Process is not ready for input.")

    def add_inference_cycles(self, num):
        if self.process and self.process.stdin:
            self.process.stdin.write(f'{num}\n')
            self.process.stdin.flush()
        else:
            print("Process is not ready for input.")

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
        rand_int = random.randint(1, 3)
        if rand_int == 1:
            self.move_left()
            self.add_to_cmd('<(*,{SELF}) --> ^left>. :|:')
        if rand_int == 2:
            self.move_right()
            self.add_to_cmd('<(*,{SELF}) --> ^right>. :|:')
        if rand_int == 3:
            self.dont_move()
            self.add_to_cmd('<(*,{SELF}) --> ^deactivate>. :|:')

    def read_line(self, out):  # read line without blocking
        for line in iter(out.readline, b'\n'):  # get operations
            if not line:  # skip empty lines
                continue
            if (line[0:3] == 'EXE'):
                subline = line.split(' ', 2)[2]
                operation = subline.split('(', 1)[0]
                if operation == '^left':
                    self.move_left()
                elif operation == '^right':
                    self.move_right()
                elif operation == '^deactivate':
                    self.dont_move()
        out.close()


class ONA(NARS):
    def __init__(self):
        super().__init__('ONA')
        self.inference_cycle_frequency = 0

    def read_line(self, out):  # read line without blocking
        for line in iter(out.readline, b'\n'):  # get operations
            if not line:  # skip empty lines
                continue
            if (line[0] == '^'):
                operation = line.split(' ', 1)[0]
                if operation == '^left':
                    self.move_left()
                elif operation == '^right':
                    self.move_right()
                elif operation == '^deactivate':
                    self.dont_move()
        out.close()
