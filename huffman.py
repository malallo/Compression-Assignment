import os
import sys
import marshal
import array
import operator

try:
    import cPickle as pickle
except:
    import pickle

def decimalToBinary(n):
    #converts from decimal to binary.
    return int("{0:b}".format(n))
        
def encode(msg):
    #first calculate the character frequency
    frequency = {}
    for character in msg:
        if not character in frequency:
            frequency[character] = 0
        frequency[character] += 1
    frequency = list(sorted(frequency.items(), key=operator.itemgetter(1)))
    tuples=[]
    for item in frequency:
        tuples.append((item[1],item[0]))
    while len(tuples)>1:#Then make the tree
        left = tuples.pop(0)
        right = tuples.pop(0)
        node = (left[0]+right[0], (left, right))
        tuples.append(node)
        tuples = list(sorted(tuples, key=operator.itemgetter(0)))
    codering = {}
    def make_ring(node, code): #Makes the coding ring recursively
        if not isinstance(node[1], tuple):
            codering[node[1]] = code
        else:
            make_ring(node[1][0], code+"1")
            make_ring(node[1][1], code+"0")
    make_ring(tuples[0], "")
    outring={}
    #Output ring should be inverse of encode ring, for key in dictionery, reverse
    for key, value in codering.items():
        outring[value] = key
    output = ""
    for character in msg:#Organizes the output
        output= output + str(codering[character])
    buffcount = 0
    while not len(output) % 8 == 0: #buffer the codewords
        output = output + "0"
        buffcount += 1
    bin_num = str(decimalToBinary(buffcount))
    i=0
    while i<(8-len(bin_num)): #Make the buffer 8 long as well
        output = output + "0"
        i+=1
    output = output + str(decimalToBinary(buffcount))
    return output, outring
    
    

def decode(msg, decoderRing): #unpads
    #have an int for length of character,
    #if it matches in dictionary,
    #move a start that far and grab the corresponding character (dictionary.get)
    length = len(msg)
    buff = msg[-8:]
    msg = msg[0:(len(msg)-(8+int(buff,2)))]
    output = ""
    code = ""
    for bit in msg:
        code = code + bit
        if code in decoderRing:
            output = output + chr(decoderRing[code])
            code = ""
    return output

def compress(msg):#First, Encode
    #Then, turn the binary encode into decimal integers and
    #then stores them as byte objects
    
    to_code, key = encode(msg)
    temp=[]
    for i in range(0, len(to_code), 8):
        temp.append(int(to_code[i:i+8],2))
    compressed = array.array('B', temp)
    return (compressed, key)

def decompress(msg, decoderRing):

    # Represent the message as an array
    byteArray = array.array('B',msg)
    enc = ""
    output = ""
    #Apparently I needed to repad my binary. It works now.
    for i in range(len(byteArray)):
        add = ""
        temp = len(str(decimalToBinary(int(byteArray[i]))))
        for j in range(8-temp):
            add = add + "0"
        add = add + str(decimalToBinary(int(byteArray[i])))
        enc = enc + add
    #once it is unpacked, decode
    output = decode(enc, decoderRing)
    output = bytes(output, 'utf-8')
    return output

def usage():
    sys.stderr.write("Usage: {} [-c|-d|-v|-w] infile outfile\n".format(sys.argv[0]))
    exit(1)

if __name__=='__main__':
    if len(sys.argv) != 4:
        usage()
    opt = sys.argv[1]
    compressing = False
    decompressing = False
    encoding = False
    decoding = False
    if opt == "-c":
        compressing = True
    elif opt == "-d":
        decompressing = True
    elif opt == "-v":
        encoding = True
    elif opt == "-w":
        decoding = True
    else:
        usage()

    infile = sys.argv[2]
    outfile = sys.argv[3]
    assert os.path.exists(infile)

    if compressing or encoding:
        fp = open(infile, 'rb')
        msg = fp.read()
        fp.close()
        if compressing:
            # cProfile.run('compress(msg)')
            compr, decoder = compress(msg)
            fcompressed = open(outfile, 'wb')
            marshal.dump((pickle.dumps(decoder), compr), fcompressed)
            fcompressed.close()
        else:
            enc, decoder = encode(msg)
            print(enc)
            fcompressed = open(outfile, 'wb')
            marshal.dump((pickle.dumps(decoder), enc), fcompressed)
            fcompressed.close()
    else:
        fp = open(infile, 'rb')
        pickleRick, compr = marshal.load(fp)
        decoder = pickle.loads(pickleRick)
        fp.close()
        if decompressing:
            msg = decompress(compr, decoder)
        else:
            msg = decode(compr, decoder)
            print(msg)
        fp = open(outfile, 'wb')
        fp.write(msg)
        fp.close()
