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
    seed = sys.argv
    if len(seed) != 2:
        print('Need exactly one parameter!')
        exit(0)
    print(simple_psw_gen(seed))
