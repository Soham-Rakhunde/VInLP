from datetime import datetime

errCodes = {
    1: 'Registration',
    2: 'Insurance',
    4: 'PUC'
}

class errorCodes:
    @staticmethod
    def decode(err=int):
        if err == 0:
            return False,'No Registration, Insurance & PUC Validity Issues'
        else:
            output = ""
            for codes in errCodes.keys():
                if codes & err == codes:
                    output += f"{', ' if output != '' else ''}{errCodes[codes]}"
            output += " date(s) exceeds validity"
            return output

    @staticmethod
    def encode(reg, ins, puc) -> int:
        now = datetime.now()
        code = int(0)
        if reg < now:
            code |= 1
        if ins < now:
            code |= 2
        if puc < now:
            code |= 4
        return code
