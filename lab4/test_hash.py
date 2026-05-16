# test_hash.py
import pytest
from hash import HashTable, HashTableCell


@pytest.fixture
def empty_table():
    """Фикстура: пустая таблица размером 20, q=1"""
    return HashTable(size=20, q=1)


@pytest.fixture
def sample_table():
    """Фикстура: таблица с несколькими предзаполненными записями"""
    ht = HashTable(size=20, q=1)
    # Используем русские ключи (географические названия)
    ht.put("Россия", "Москва")
    ht.put("Волга", "река")
    ht.put("Альпы", "горы")
    # Добавляем ключ, который вызовет коллизию (хеш-адрес совпадает с "Россия"? Подбираем)
    # Для демонстрации: подберём ключ с тем же h, что у "Россия" (V=Р*33+о=17*33+14=575, 575%20=15)
    # Ключ "Рим" (Р=17, и=8) -> V=17*33+8=569, 569%20=9 (не 15). "Рейн" (Р=17, е=5) -> 566%20=6.
    # "Урал" (У=20, р=17) -> 20*33+17=677, 677%20=17. Не подходит. Вставим "Россия2"? Но нужно два символа.
    # Для теста коллизий создадим отдельный тест.
    return ht


class TestHashTableCell:
    def test_cell_initial_state(self):
        cell = HashTableCell()
        assert cell.id == ""
        assert cell.pi == ""
        assert cell.u == 0
        assert cell.v == -1
        assert cell.h == -1
        assert cell.d == 0
        assert cell.checkU() is True   # u==0 значит свободна
        assert cell.checkD() is False

    def test_cell_update(self):
        cell = HashTableCell()
        cell.update("Россия", "Москва", 575, 15)
        assert cell.id == "Россия"
        assert cell.pi == "Москва"
        assert cell.u == 1
        assert cell.v == 575
        assert cell.h == 15
        assert cell.d == 0
        assert cell.checkU() is False   # теперь занята
        assert cell.checkD() is False


class TestHashTableInit:
    def test_default_parameters(self):
        ht = HashTable()
        assert ht.size == 20
        assert ht.q == 1
        assert len(ht.table) == 20
        for cell in ht.table:
            assert cell.u == 0

    def test_custom_parameters(self):
        ht = HashTable(size=31, q=2)
        assert ht.size == 31
        assert ht.q == 2
        assert len(ht.table) == 31


class TestHashFunctions:
    def test_symbolToNum(self, empty_table):
        alphabet = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
        for idx, ch in enumerate(alphabet):
            assert empty_table._symbolToNum(ch) == idx
        # Проверка с маленькой буквой
        assert empty_table._symbolToNum("а") == 0
        assert empty_table._symbolToNum("я") == 32
        # Проверка с буквой Ё
        assert empty_table._symbolToNum("Ё") == 6   # позиция Ё в алфавите

    def test_keyToNum(self, empty_table):
        # Россия: Р=17, о=15 -> 17*33+15 = 576
        assert empty_table._keyToNum("Россия") == 576
        # Волга: В=2, о=15 -> 2*33+14 = 80
        assert empty_table._keyToNum("Волга") == 81
        # Альпы: А=0, л=12 -> 0*33+12 = 12
        assert empty_table._keyToNum("Альпы") == 12
        # Короткий ключ из двух букв
        assert empty_table._keyToNum("АЗ") == 8

    def test_hash(self, empty_table):
        assert empty_table._hash(575) == 575 % 20 == 15
        assert empty_table._hash(80) == 80 % 20 == 0
        assert empty_table._hash(12) == 12 % 20 == 12
        # С другим размером
        ht = HashTable(size=31)
        assert ht._hash(575) == 575 % 31 == 17


class TestInsertAndSearch:
    def test_insert_into_free_cell(self, empty_table):
        v = 575
        h = empty_table._hash(v)
        assert empty_table._insert(h, "Россия", "Москва", v, h) is True
        cell = empty_table.table[h]
        assert cell.id == "Россия"
        assert cell.pi == "Москва"
        assert cell.u == 1
        assert cell.v == v
        assert cell.h == h

    def test_insert_into_deleted_cell(self, empty_table):
        # Сначала вставляем, потом удаляем (помечаем d=1)
        v = 575
        h = empty_table._hash(v)
        empty_table._insert(h, "Россия", "Москва", v, h)
        empty_table.table[h].d = 1   # удалили
        # Теперь вставляем новый ключ в ту же ячейку
        v2 = 80
        h2 = empty_table._hash(v2)  # может быть другим, но мы принудительно вставим в тот же index
        assert empty_table._insert(h, "Волга", "река", v2, h) is True
        cell = empty_table.table[h]
        assert cell.id == "Волга"
        assert cell.pi == "река"
        assert cell.u == 1
        assert cell.d == 0

    def test_insert_into_occupied_cell_returns_false(self, empty_table):
        v = 575
        h = empty_table._hash(v)
        empty_table._insert(h, "Россия", "Москва", v, h)
        # Попытка вставить другой ключ в ту же ячейку
        v2 = 80
        assert empty_table._insert(h, "Волга", "река", v2, h) is False
        # Ячейка не изменилась
        assert empty_table.table[h].id == "Россия"

    def test_search_existing_key(self, sample_table):
        # Поиск существующего ключа
        idx = sample_table._search("Россия")
        assert idx != -1
        assert sample_table.table[idx].id == "Россия"
        # Поиск после удаления
        sample_table.delete("Волга")
        idx = sample_table._search("Волга")
        assert idx == -1   # удалённый ключ не должен находиться

    def test_search_nonexistent_key(self, empty_table):
        assert empty_table._search("Нева") == -1

    def test_put_new_key(self, empty_table):
        empty_table.put("Россия", "Москва")
        idx = empty_table._search("Россия")
        assert idx != -1
        assert empty_table.table[idx].pi == "Москва"

    def test_put_duplicate_key_raises_exception(self, sample_table):
        with pytest.raises(Exception, match="Запись с таким ключем уже есть"):
            sample_table.put("Россия", "Санкт-Петербург")

    def test_put_collision_handling(self, empty_table):
        # Найдём два ключа с одинаковым хешем
        # Хеш = V % 20. V = код1*33+код2.
        # Подберём: "Россия" V=575, h=15. Ищем другой ключ с h=15: нужно V ≡ 15 (mod 20)
        # V = 20k+15. Перебираем возможные первые буквы:
        # Для "?а": V = код1*33+0. 33*код1 mod 20 = (33 mod20=13)*код1 mod20. 13*код1 ≡15 mod20.
        # код1=5 (буква Е? Е=5) -> 13*5=65≡5, нет. код1=15 (Н? Н=14? Алфавит: А0,Б1,В2,Г3,Д4,Е5,Ё6,Ж7,З8,И9,Й10,К11,Л12,М13,Н14,О15,П16,Р17,С18,Т19,У20,Ф21,Х22,Ц23,Ч24,Ш25,Щ26,Ъ27,Ы28,Ь29,Э30,Ю31,Я32). О=15 -> 13*15=195≡15, подходит. Тогда V=15*33+? =495+? =? нужно 20k+15. 495+? ≡15 mod20 -> 495≡15 mod20, значит ? должно быть кратно 20. ?=0 (буква А) -> V=495, 495%20=15. Ключ "ОА"? Не очень. Второй вариант: ключ "Оа" – но в русском нет. Лучше использовать "ОА" как аббревиатуру. Вставим "ОА" (О=15, А=0) -> V=495, h=15. Теперь вставим "Россия" (h=15) и "ОА" – коллизия.
        empty_table.put("Россия", "Москва")
        empty_table.put("ОА", "ОАЭ")  # коллизия с Россией
        # Проверим, что оба ключа в таблице
        assert empty_table._search("Россия") != -1
        assert empty_table._search("ОА") != -1
        # Они должны быть в разных ячейках (например, Россия на 15, ОА на 16)
        idx_rus = empty_table._search("Россия")
        idx_oa = empty_table._search("ОА")
        assert idx_rus != idx_oa

    def test_put_table_full(self, empty_table):
        # Заполним всю таблицу (size=20) разными ключами, чтобы не было коллизий
        # Используем ключи вида "АА", "АБ", ... (но нужно русские)
        for i in range(20):
            # Формируем ключ из двух букв: первая буква - 'А' (0), вторая - буква с номером i
            alphabet = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
            key = "А" + alphabet[i % 33]
            empty_table.put(key, str(i))
        # Таблица заполнена (все ячейки заняты)
        with pytest.raises(Exception, match="Нет места для вставки"):
            empty_table.put("БА", "лишний")

    def test_delete_existing_key(self, sample_table):
        sample_table.delete("Россия")
        idx = sample_table._search("Россия")
        assert idx == -1
        # Ячейка должна иметь флаг d=1
        # Найдём ячейку, где был ключ – она осталась занятой с d=1
        # Но _search игнорирует удалённые, так что прямой доступ:
        cell = sample_table.table[sample_table._hash(sample_table._keyToNum("Россия"))]
        # Однако при коллизиях ячейка может быть не на основном адресе. Проще проверить, что у всех ячеек с id="Россия" d=1
        found = False
        for cell in sample_table.table:
            if cell.id == "Россия":
                assert cell.d == 1
                found = True
        assert found

    def test_delete_nonexistent_key(self, empty_table):
        with pytest.raises(Exception, match="Нет элемента для удаления"):
            empty_table.delete("Нева")

    def test_delete_already_deleted_key(self, sample_table):
        sample_table.delete("Россия")
        with pytest.raises(Exception, match="Нет элемента для удаления"):
            sample_table.delete("Россия")

    def test_get_existing_key(self, sample_table):
        assert sample_table.get("Россия") == "Москва"
        assert sample_table.get("Волга") == "река"

    def test_get_nonexistent_key(self, empty_table):
        with pytest.raises(Exception, match="Нет элемента c таким ключем"):
            empty_table.get("Нева")

    def test_get_deleted_key(self, sample_table):
        sample_table.delete("Волга")
        with pytest.raises(Exception, match="Нет элемента c таким ключем"):
            sample_table.get("Волга")

    def test_display_does_not_crash(self, sample_table, capsys):
        sample_table.display()
        captured = capsys.readouterr()
        assert "Россия" in captured.out
        assert "Волга" in captured.out
        assert "Альпы" in captured.out
        assert "=" in captured.out


class TestCollisionsAndProbing:
    def test_linear_probing_sequence(self, empty_table):
        # Создаём несколько ключей с одинаковым хешем
        # Используем "Россия" (h=15), "ОА" (h=15), "ПА" (П=16, А=0 -> 16*33+0=528%20=8? не 15)
        # Подберём третий ключ с h=15. Формула: (k1*33 + k2) %20 =15. Перебирать вручную долго.
        # Для теста достаточно двух коллизий.
        empty_table.put("Россия", "Москва")
        empty_table.put("ОБ", "ОАЭ")  # коллизия
        # Проверим, что при поиске второго ключа пробирование работает (начинаем с h и идём дальше)
        idx = empty_table._search("ОБ")
        assert idx != -1
        # Убедимся, что ячейка не равна исходному хешу (если была коллизия, то должна быть сдвинута)
        h_oa = empty_table._hash(empty_table._keyToNum("ОБ"))  # 15
        assert idx != h_oa
        # Теперь удалим первый ключ ("Россия") и проверим, что поиск второго всё ещё работает
        empty_table.delete("Россия")
        idx2 = empty_table._search("ОБ")
        assert idx2 == idx   # должен найти на том же месте

    def test_put_update_not_allowed(self, sample_table):
        # В текущей реализации put не позволяет обновить существующий ключ (бросает исключение)
        with pytest.raises(Exception, match="Запись с таким ключем уже есть"):
            sample_table.put("Россия", "Новое значение")

    def test_put_after_delete_reuses_cell(self, empty_table):
        # Вставляем ключ, удаляем его, затем вставляем новый ключ (с тем же хешем или другим)
        empty_table.put("Россия", "Москва")
        h_rus = empty_table._hash(empty_table._keyToNum("Россия"))
        empty_table.delete("Россия")
        # Теперь вставляем другой ключ, который должен занять освободившуюся ячейку (если его хеш ведёт туда же или при коллизии)
        # Используем ключ с тем же хешем, чтобы он гарантированно попал на ту же ячейку при линейном пробировании
        # "ОА" имеет хеш 15, как и "Россия"
        empty_table.put("ОБ", "ОАЭ")
        idx = empty_table._search("ОБ")
        assert idx == h_rus   # должна быть та же ячейка
        # Проверим, что старая запись полностью затерта (флаг d=0, id="ОА")
        cell = empty_table.table[idx]
        assert cell.id == "ОБ"
        assert cell.d == 0
