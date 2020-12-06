def calc_checksum(hex_str):
    """ Returns a string of the 2 comps 8 bit checksum
    input is the payload string which the check sum shall be calculated from
    """
    pld = [hex_str[i:i+2] for i in range(0,len(hex_str),2)]
    l = (len(hex_str)/2.0)
#    if ~l.is_integer():
#        print('No half bytes')
#        return 0
    sum = 0
    for h in pld:
        sum += int(h,16) 
    chk = 0x100 - int(hex(sum)[-2:],16)
    return hex(chk)[2:].zfill(2)
