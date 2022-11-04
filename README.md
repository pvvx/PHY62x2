Utils for PHY62x2

### Pins: USB-COM / Board

DTR->TM

RTS->RSTN

TX->RX

RX<-TX

### Usage

```
usage: rdreg_phy6202 [-h] [--port PORT] [--baud BAUD] address size

RdRegs-PHY6202 Utility version 30.11.19-2

positional arguments:
  address               Start address
  size                  Size of region to dump

options:
  -h, --help            show this help message and exit
  --port PORT, -p PORT  Serial port device
  --baud BAUD, -b BAUD  Set Baud
```

```
usage: WrFlash_phy6202 [-h] [--port PORT] [--baud BAUD] [--chiperase]
                       address filename
WrFlash-PHY6202 Utility version 07.12.19

positional arguments:
  address               Start Flash address
  filename              File name

options:
  -h, --help            show this help message and exit
  --port PORT, -p PORT  Serial port device
  --baud BAUD, -b BAUD  Set Port Baud (115200, 250000, 500000, 1000000)
  --chiperase, -c       All Chip Erase
```

### Read all Flash

```
python3 rdreg_phy6202.py -p COM5 -b 1000000 0x11000000 0x80000
```

### Write all Flash

```
python3 write_phy6202.py -p COM18 -c -b 500000 0 r11000000-00080000.bin
```
