from hash import HashTable


def main():
    hs = HashTable()
    print('#1 Clear full table: clr; <size>; <q>')
    print('#2 Add record: add; <key>; <value>')
    print('#3 Delete record: del; <key>')
    print('#4 Get record: get; <key>')
    print('#5 Display table: dsp')
    print('#6 Delete record: ext')
    print('_________________________________\n')
    
    while True:
        try:
            choice = input('> ')
            
            match choice[:3]:
                case 'clr':
                    _, size, q = choice.split('; ')
                    hs = HashTable(int(size), int(q))
                case 'add':
                    _, key, val = choice.split('; ')
                    hs.put(key, val)
                case 'del':
                    _, key = choice.split('; ')
                    hs.delete(key)
                case 'get':
                    _, key = choice.split('; ')
                    val = hs.get(key)
                    print('value: ', val)
                case 'dsp':
                    hs.display()
                case 'ext':
                    return
                case _:
                    print("Неизвестная команда. Попробуйте: clr, add, del, get, dsp, ext")
        except Exception as e:
            print(f"Ошибка: {e}")

        


if __name__ == "__main__":
    main()
