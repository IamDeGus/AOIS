from src import Binary_float

def main():
    a = Binary_float('4')
    print('a:', str(a))
    b = Binary_float('2')
    print('b:', str(b))
    c = a + b
    print('--\nc:', str(c))

if __name__ == "__main__":
    main()
