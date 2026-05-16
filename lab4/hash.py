from dataclasses import dataclass


@dataclass
class HashTableCell:
    id: str = ""
    pi: str = ""
    u: int = 0
    v: int = -1
    h: int = -1
    d: int = 0

    def checkU(self) -> bool:
        return self.u == 0

    def checkD(self) -> bool:
        return self.d == 1

    def update(self, id: str, pi: str, v: int, h: int) -> None:
        self.id = id
        self.pi = pi
        self.u = 1
        self.v = v
        self.h = h
        self.d = 0


class HashTable:

    def __init__(self, size: int = 20, q: int = 1) -> None:
        self.size = size
        self.q = q
        self.table = [HashTableCell() for _ in range(self.size)]

    def _symbolToNum(self, s: str) -> int:
        alphabet = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
        return alphabet.index(s.upper())

    def _keyToNum(self, key: str) -> int:
        s1 = self._symbolToNum(key[0])
        s2 = self._symbolToNum(key[1])
        return s1 * 33 + s2

    def _hash(self, number: int) -> int:
        return number % self.size

    def _insert(self, index: int, key: str, value: str, v: int, h: int) -> bool:
        if self.table[index].checkU() or self.table[index].checkD():
            self.table[index].update(key, value, v, h)
            return True
        return False

    def _search(self, key: str) -> int:
        v = self._keyToNum(key)
        h = self._hash(v)
        index = h

        while not self.table[index].checkU():
            if self.table[index].id == key and not self.table[index].checkD():
                return index

            index = (index + self.q) % self.size

            if index == h:
                return -1

        return -1

    def put(self, key: str, value: str) -> None:
        if not self._search(key) == -1:
            raise Exception("Запись с таким ключем уже есть")
        
        v = self._keyToNum(key)
        h = self._hash(v)

        index = h

        if self._insert(index, key, value, v, h):
            return

        index = (index + self.q) % self.size

        while index != h:
            if self._insert(index, key, value, v, h):
                return
            index = (index + self.q) % self.size

        raise Exception("Нет места для вставки")

    def delete(self, key: str) -> None:
        index = self._search(key)
        if index == -1:
            raise Exception("Нет элемента для удаления")

        self.table[index].d = 1

    def display(self) -> None:
        print("\n" + "=" * 90)
        print(
            f"{'№':<3} {'Ключ':<20} {'Данные':<30} {'V':<8} {'h':<4} {'U':<2} {'D':<2}")
        print("-" * 90)
        for i in range(self.size):
            row = self.table[i]
            print(
                f"{i:<3} {row.id:<20} {str(row.pi)[:30]:<30} {row.v:<8} {row.h:<4} {row.u:<2} {row.d:<2}")

        print("=" * 90)

    def get(self, key: str) -> str:
        index = self._search(key)
        if index == -1:
            raise Exception("Нет элемента c таким ключем")

        return self.table[index].pi
