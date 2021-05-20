from datetime import datetime

errCodes = {
    1: 'Registration',
    2: 'Insurance',
    4: 'PUC',
}

class errorCodes:
    @staticmethod
    def decode(err=int):
        if err == 0:
            return 'No Registration, Insurance & PUC Validity Issues'
        else:
            output = ""
            for codes in errCodes.keys():
                if codes & err == codes:
                    output += f"{', ' if output != '' else ''}{errCodes[codes]}"
            output += " date(s) exceeds validity"
            return output

    @staticmethod
    def encode(reg, ins, puc) -> int:
        code = int(0)
        now = datetime.now()
        if reg != 'NA':
            regDT = datetime.strptime(reg, '%d-%b-%Y')
            if regDT < now:
                code |= 1
        else:
            code |= 1
        if ins != 'NA':
            insDT = datetime.strptime(ins, '%d-%b-%Y')
            if insDT < now:
                code |= 2
        else:
            code |= 2
        if puc != 'NA':
            pucDT = datetime.strptime(puc, '%d-%b-%Y')
            if pucDT < now:
                code |= 4
        else:
            code |= 4

        return code
