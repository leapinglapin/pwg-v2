

class upcbar:

    def __init__(self, barcode):
        self.barcode = str(barcode)

    def get_prefix(self):
        if len(self.barcode) >14:
            return self.barcode
        elif len(self.barcode) == 14:
            return self.barcode[0:7]
        elif len(self.barcode) == 13:
            return self.barcode[0:7]
        elif len(self.barcode) == 12:
            return '0' + self.barcode[0:6]
        elif len(self.barcode) < 8:
            return '00' + self.barcode[0:6]
