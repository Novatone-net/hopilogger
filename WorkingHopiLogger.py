import struct
import serial
import time
import csv
import msvcrt
import os.path

#Super lightweight code to read Hopi HP-9800 power meter

class Hopi(object):

    REGS=[
            ("Active Power","W"),
            ("RMS Current","A"),
            ("Voltage RMS","V"),
            ("Frequency","Hz"),
            ("Power Factor","pf"),
            ("Annual Power","KWH"),
            ("Active Power","KWH"),
            ("Reactive Power","KWH"),
            ("Load Time","mins"),
        ]
    FIELDS=[
            ("Active Power W"),
            ("RMS Current A"),
            ("Voltage RMS V"),
            ("Frequency Hz"),
            ("Power Factor"),
            ("Annual Power KWH"),
            ("Active Power KWH"),
            ("Reactive Power KWH"),
            ("Load Time Min."),

        ]

    def __init__(self,port="COM4"):
        baud=9600
        self.debug=True #False #True
        
        self.ser=serial.Serial(port,baudrate=baud,timeout=1)
    
    def crc(self,data):
        poly=0xa001
        crc = 0xFFFF
        for b in data:
            cur_byte = 0xFF & b
            for _ in range(0, 8):
                if (crc & 0x0001) ^ (cur_byte & 0x0001):
                    crc = (crc >> 1) ^ poly
                else:
                    crc >>= 1
                cur_byte >>= 1
        print(crc&0xffff)
        return struct.pack("<H",crc&0xffff)
    
    def read(self):
        self.readRegs(4,2) #1,10) # register start number, count (4,2) default (finds the registers?)
        if self.debug:
            print ("length:", len(self.REGS)*2)
        self.regs=self.readRegs(0,len(self.REGS)*2) #1,10)
        
    def display(self):
        dmax=99 #can limit how many regs displayed

        if self.regs is not None:
            for idx,value in enumerate(self.regs):
                name,unit=self.REGS[idx]
                print ("%s\t%.3f%s" % (name,value,unit))
                dmax-=1
                if dmax==0:
                    break

    def fillfields(self):
        dmax=99 #can limit how many regs displayed

        if self.regs is not None:
            for idx,value in enumerate(self.regs):
                name,unit=self.REGS[idx]
                self.FIELDS[idx] = value
                
                #print("%.3f" % (value))
                dmax-=1
                if dmax==0:
                    break

    def phex(self,data):
        s=" ".join(["%02x" % d for d in data])
        return s
        
    def readRegs(self,first,count,addr=1):
        cmd=0x03
        fout=[]
        m=struct.pack(">BBHH",addr,cmd,first,count)
        m+=self.crc(m)
        if self.debug:
            print ("\t>",self.phex(m))
        self.ser.write(m)
        replyLen=3+(count*2)+2
        r=self.ser.read(replyLen)
        if self.debug:
            print ("\t<",self.phex(r))
        if len(r)!=replyLen:
            print ("Bad reply len",len(r))
            return
        ccrc=self.crc( r[:-2] )

        if ccrc!=r[-2:]:
            print ("bad crc (in response because the code doesn't work)")
            #return
        addr,f,bcount=struct.unpack(">BBB",r[:3])
        if addr==addr and f==cmd:
            #unpack floats from hopi
            d=r[3:-2]
            fpos=0
            while fpos<len(d):
                fpval=d[fpos:fpos+4]
                v=struct.unpack("<f",fpval)[0]
                fout.append(v)
                fpos+=4
                #print fpos/2,v
            return fout
        else:
            print ("Bad reply")
            
            
        
h=Hopi(port="COM4")
# name of csv file 
filename = "hopilog.csv"
    
if not os.path.isfile(filename):    
    # write headers to csv file
    with open(filename, 'a', newline='', buffering=-1) as csvfile: 
        # creating a csv writer object 
        csvwriter = csv.writer(csvfile) 
            
        # writing the fields 
        csvwriter.writerow(h.FIELDS) 
        # the end of the 'with' implicitly closes the file

while True:
    h.read()
    h.display()
    h.fillfields()
    if h.debug:
        print (h.FIELDS)

    # writing to csv file 
    with open(filename, 'a', newline='', buffering=-1) as csvfile: 
        # creating a csv writer object 
        csvwriter = csv.writer(csvfile) 
            
        # writing the data rows 
        csvwriter.writerow(h.FIELDS)
        # the end of the 'with' implicitly closes the file

    # Set log frequency here in seconds
    time.sleep(10)
  
