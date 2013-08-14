class UnitConverter(object):
    SIZE_UNITS = {
        'K': 1024,
        'M': 1024 * 1024,
        'G': 1024 * 1024 * 1024,
        'P': 1024 * 1024 * 1024 * 1024,
        'E': 1024 * 1024 * 1024 * 1024 * 1024
        }
    
    @classmethod
    def string_to_bytes(cls, str):
        if len(str) == 0:
            raise ValueError("Emtpy size string")

        if str.isdigit():
            return int(str)

        num = str[0:-1]
        unit = str[-1]

        if not num.isdigit():
            raise ValueError("Invalid size string")

        if not unit in cls.SIZE_UNITS:
            raise ValueError("Unknown size unit")

        return cls.SIZE_UNITS[unit] * int(num)
