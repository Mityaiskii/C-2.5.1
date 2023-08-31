from random import randint


class BoardExemptions(Exception):
    pass
class OutOfBoard(BoardExemptions):
    def __str__(self):
        return 'Введите координаты в пределах игрового поля!'


class CellIsBusy(BoardExemptions):
    def __str__(self):
        return 'Клетка уже занята!'


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f'{self.x, self.y}'


class Ship:
    def __init__(self, bow: Dot, size, d):
        self.bow = bow
        self.size = size
        self.d = d
        self.hp = size

    @property
    def dots(self):
        ship_dots = []
        dot_x = self.bow.x
        dot_y = self.bow.y
        for i in range(self.size):
            ship_dots.append(Dot(dot_x - 1, dot_y - 1))
            if self.d == 0:
                dot_y += 1
            elif self.d == 1:
                dot_x += 1

        return ship_dots


class Board:
    def __init__(self, size=6, hid=False):
        self.size = size
        self.hid = hid
        self.count = 0
        self.field = [[' '] * size for i in range(size)]
        self.busy = []
        self.ships = []

    def __str__(self):
        rows = ['A','B', 'C', 'D', 'E', 'F']
        columns = '   1 | 2 | 3 | 4 | 5 | 6 |'
        for i, row in enumerate(self.field):
            columns += f'\n{rows[i]}| '+' | '.join(self.field[i]) + ' |'
        if self.hid:
            columns = columns.replace('■', ' ')
        return columns

    def add_ship(self, ship: Ship):

        for dot in ship.dots:
            if self.out(dot):
                raise OutOfBoard
            if dot in self.busy:
                raise CellIsBusy
        for dot in ship.dots:
            self.field[dot.x][dot.y] = '■'
            self.busy.append(dot)

        self.ships.append(ship)
        self.contour(ship)

    def out(self, dot: Dot):
        return not((0 <= dot.x < self.size) and (0 <= dot.y < self.size))

    def contour(self, ship: Ship, vis = False):
        contour = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                contour.append((i, j))
        for d in ship.dots:
            for dx, dy in contour:
                check = Dot(d.x + dx, d.y + dy)
                if not (self.out(check)) and check not in self.busy:
                    if vis:
                        self.field[check.x][check.y] = '.'
                    self.busy.append(check)

    def shot(self, dot: Dot):
        if self.out(dot):
            raise OutOfBoard
        if dot in self.busy:
            raise CellIsBusy
        self.busy.append(dot)
        for ship in self.ships:
            if dot in ship.dots:
                self.field[dot.x][dot.y] = 'Х'
                ship.hp -= 1
                if ship.hp == 0:
                    self.count += 1
                    print('Убит!')
                    return False
                else:
                    print('Ранен!')
                    return True

        self.field[dot.x][dot.y] = '.'
        print('Мимо!')
        return False

    def begin(self):
        self.busy = []


class Player:
    def __init__(self, board: Board, enemy: Board):
        self.board = board
        self.enemy = enemy
    def ask(self):
        pass
    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardExemptions as e:
                print(e)

class AI(Player):
    def ask(self):
        letters = ['A', 'B', 'C', 'D', 'E', 'F']
        d = Dot(randint(0, 5), randint(0, 5))
        print(f'Ход компьютера: {letters[d.x]}{d.y + 1}')
        return d

class User(Player):
    def ask(self):
        letters = ['A', 'B', 'C', 'D', 'E', 'F']
        while True:
            req = input('Введите координаты в формате "A1":')
            if len(req) != 2 or req[0].upper() not in letters or not (req[1].isdigit()):
                print('Введите корректное значение!')

            elif 1 > int(req[1]) or int(req[1]) > 6:
                print('Введите корректное значение!')
            else:
                x, y = req[0].upper(), int(req[1])
                x = letters.index(x)
                y -= 1
                d = Dot(x, y)
                print(f'Ход игрока: {letters[d.x]}{d.y + 1}')
                return d
class Game:

    def __init__(self, size=6):
        self.size = size
        us_map = self.random_board()
        ai_map = self.random_board()
        ai_map.hid = True

        self.us = User(us_map, ai_map)
        self.ai = AI(ai_map, us_map)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        ships = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for i in ships:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, 5), randint(0, 5)), i, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardExemptions:
                    pass

        board.begin()
        return board

    def greet(self):
        print('-------------------')
        print('Морской бой')
        print('Формат ввода: A1')
        print('-------------------')

    def loop(self):
        num = 0
        while True:
            print('Доска пользователя:')
            print(self.us.board)
            print('Доска компьютера:')
            print(self.ai.board)
            if num % 2 == 0:
                print('Ходит пользователь!')
                repeat = self.us.move()
            else:
                print("-" * 20)
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1
            if self.ai.board.count == 7:
                print('Пользователь выиграл!')
                break
            if self.us.board.count == 7:
                print('Компьютер выиграл!')
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()











