from random import randint
import time

class BoardException(Exception):
    pass

class BoardOutException(BoardException):
    def __str__(self):
        return "Вы стреляете мимо доски!"

class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку!"

class BoardWrongDotException(BoardException):
    pass

class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f'Dot ({self.x}, {self.y})'

class Ship:
    def __init__(self, head, l, a):
        self.head = head
        self.l = l
        self.a = a
        self.lives = l


    @property
    def desk(self):
        ship_dots = []
        for i in range(self.l):
            cur_x = self.head.x
            cur_y = self.head.y

            if self.a == 0:
                cur_x += i
            elif self.a == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))
        return ship_dots

    def shooten(self, shot):
        return shot in self.desk

class Board:
    def __init__(self, hid=False, size=6):

        self.hid = hid
        self.size = size

        self.count = 0
        self.see = [['|О|'] * size for _ in range(size)]

        self.busy = []
        self.ships = []


    def __str__(self):
        res = ''
        res += '   1   2   3   4   5   6'
        for i, row in enumerate(self.see):
            res += f'\n{i + 1}' + " ".join(row)

        if self.hid:
            res = res.replace('|■|','|0|')
        return res


    def out(self, d):
        return not((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def contour(self, ship, verb=False):
        near = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
        for d in ship.desk:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not(self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.see[cur.x][cur.y] = '|.|'
                    self.busy.append(cur)

    def add_ship(self, ship):
        for d in ship.desk:
            if self.out(d) or d in self.busy:
                raise BoardWrongDotException()
        for d in ship.desk:
            self.see[d.x][d.y] = '|■|'
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardUsedException()

        self.busy.append(d)

        for ship in self.ships:
            if d in ship.desk:
                ship.lives -= 1
                self.see[d.x][d.y] = "|X|"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print('Корабль уничтожен!')
                    return False
                else:
                    print("Корабль ранен!")
                    return True

        self.see[d.x][d.y] = "|.|"
        print("Мимо!")
        return False

    def begin(self):
        self.busy = []

class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)

class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f'Ход ИИ: {d.x + 1} {d.y + 1}')
        return d

class Human(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход").split()
            if len(cords) != 2:
                print('Вы забыли ввести вторую координату!')
                continue

            x, y = cords

            if not(x.isdigit()) or not (y.isdigit()):
                print('Это не числа!')
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)

class Game:
    def try_board(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts == 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongDotException:
                    pass

        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = AI(co, pl)
        self.hm = Human(pl, co)

    def greet(self):
        print("Добро пожаловать в игру 'Морской бой!'")
        print('Введите координаты клетки (от 1 до 6): x - номер строки, y - номер столбца')

    def loop(self):
        num = 0
        while True:
            print('-' * 20)
            print('Ваша доска:')
            print(self.hm.board)
            print('-' * 20)
            print('Доска ИИ:')
            print(self.ai.board)
            print('-' * 20)
            if num % 2 == 0:
                print('Ходит человек!')
                repeat = self.hm.move()
                time.sleep(1)
            else:
                print('Ходит ИИ!')
                time.sleep(3)
                repeat = self.ai.move()
                time.sleep(1)
            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print('_' * 20)
                print('Поздравляем, Вы выиграли!')
                break

            if self.hm.board.count == 7:
                print('_' * 20)
                print('ИИ выиграл!')
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


