import hashlib
import base64
import sys


# A super simple passward generator
# generated passward contain both upper/lower case english letter, number and special character.
def simple_psw_gen(seed: [str, int]) -> str:
    string = str(seed)
    md5 = hashlib.md5(string.encode(encoding='utf-8')).digest()
    b64 = base64.b64encode(md5)
    return b64[:-2].decode()

if __name__ == '__main__':
    args = sys.argv
    if len(args) > 2:
        print('Need exactly one parameter!')
        exit(0)
    elif len(args) == 1:
        wait = True
        seed = input("Enter the seed: ")
    else:
        seed = args[1]
    print(simple_psw_gen(seed))
    if wait:
        input("Press Enter to exit...")
