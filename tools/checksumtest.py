
def checksum_2_com(hex_str):
    num = len(hex_str)
    if num%2 != 0:
        print('No half bytes!!')
        return 0
    sum = hex(0)
    for i in range(0,num/2+2,2):
        print(i)
        sum = hex(int(hex_str[i:i+2],16) + int(sum,16))
    cks = hex(0x100 + int(sum,16))
    return cks
