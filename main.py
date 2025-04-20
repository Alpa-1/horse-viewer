from typing import NamedTuple
import pikepdf
from datetime import datetime
from pprint import pprint
from enum import StrEnum
from statistics import mean
from pdfminer.high_level import extract_text

RANK_ICON_WIDTH = 52

class RankType(StrEnum):
    D_MINUS = "D-"
    D = "D"
    D_PLUS = "D+"
    C_MINUS = "C-"
    C = "C"
    C_PLUS = "C+"
    B_MINUS = "B-"
    B = "B"
    B_PLUS = "B+"
    A_MINUS = "A-"
    A = "A"
    A_PLUS = "A+"
    S_MINUS = "S-"
    S = "S"
    S_PLUS = "S+"
    SS_MINUS = "SS-"
    SS = "SS"
    SS_PLUS = "SS+"
    SSS_MINUS = "SSS-"
    SSS = "SSS"
    SSS_PLUS = "SSS+"


class AttributeName(StrEnum):
    START = "START"
    SPEED = "SPEED"
    STAMINA = "STAMINA"
    FINISH = "FINISH"
    HEART = "HEART"
    TEMPER = "TEMPER"

NAMES = ["START", "SPEED", "STAMINA", "FINISH", "HEART", "TEMPER"]




class Candle:
    minimum: float
    median: float
    maximum: float

    def __init__(self, minimum: float, min_origin: float, median: float, median_origin: float, maximum: float, max_origin: float):
        self.bottom = minimum - 2
        self.minimum = minimum
        self._min_origin = min_origin
        self.median = median
        self._median_origin = median_origin
        self.maximum = maximum
        self._max_origin = max_origin
        self.top = maximum + 2

    def __str__(self):
        return f"MIN {self._min_origin}: {self.minimum}, MED {self._median_origin}: {self.median}, MAX {self._max_origin}: {self.maximum}"
    def __repr__(self):
        return self.__str__()


class Origin(NamedTuple):
    x: float
    y: float

class _Rectangle:
    name: str
    origin: Origin
    rectangle: pikepdf.Rectangle

    def __init__(self, name: str, origin: Origin, rectangle: pikepdf.Rectangle):
        self.name = name
        self.origin = origin
        self.rectangle = rectangle

    def __repr__(self):
        return f"{self.name}: {self.origin}, {self.rectangle}"

class Rank:
    name: RankType

    def __init__(self, name: RankType, xmin: float, xmax: float):
        self.name = name
        self._xmin = xmin
        self._xmax = xmax

    def __repr__(self):
        return f"{self.name.value}: {self._xmin} - {self._xmax}"
    
    def __contains__(self, value: float) -> bool:
        return self._xmin <= value <= self._xmax

class _Ranks:
    d: float
    c: float
    b: float
    a: float
    s: float
    ss: float
    sss: float

    _total_mean: float
    _section: float
    _offset: float

    def __init__(self, d: float, c: float, b: float, a: float, s: float, ss: float, sss: float):
        if not d < c < b < a < s < ss < sss:
            raise ValueError("Invalid rank order")

        self.d = d
        self.c = c
        self.b = b
        self.a = a
        self.s = s
        self.ss = ss
        self.sss = sss
        self._total_mean = mean([sss-ss, ss-s, s-a, a-b, b-c, c-d])
        self._section = self._total_mean / 3
        self._offset = ( self._total_mean - RANK_ICON_WIDTH ) / 2
    
    def __repr__(self):
        return f"D: {self.d}, C: {self.c}, B: {self.b}, A: {self.a}, S: {self.s}, SS: {self.ss}, SSS: {self.sss}, MEAN: {self._total_mean}, SECTION: {self._section}, OFFSET: {self._offset}"

class Attribute:
    name: AttributeName

    def __init__(self, name: AttributeName, values: Candle):
        self.name = name
        self.values = values


    def at(self, x: float, ranks: list[Rank]) -> RankType:
        for rank in ranks:
            if x in rank:
                return rank.name
        raise ValueError(f"Value {x} not in any rank")

    def __repr__(self):
        return f"{self.name}: {self.values}"

def parse_rectangles(rectangles: list[_Rectangle]) -> dict[AttributeName, Candle]:
    interesting: dict[AttributeName, Candle] = {}

    candle_values = []
    count = 0
    max_count = len(NAMES)
    capture = False
    for rect in rectangles:
        if rect.rectangle.width == 500:
            # print(f"Discarding rectangle with width 500: {rect}")
            continue
        if rect.rectangle.width == 2 and rect.rectangle.height == 30 and capture:

            if len(candle_values) != 6:
                print(f"Invalid number (!=6) of candle values: {candle_values}")
                break
            interesting[AttributeName(NAMES[count])] = Candle(*candle_values)
            candle_values = []
            count += 1
            capture = False
            continue
            
        if rect.rectangle.width == 2 and rect.rectangle.height == 30:
            capture = True
            continue

        if not capture:
            continue

        if count >= max_count:
            print(f"Too many viable rectangle groups found found: {count}")
            break

        candle_values.append(rect.rectangle.width)
        candle_values.append(rect.origin.x)

    return interesting

def parse(file: str) -> tuple[list[Attribute], list[Rank]]:
    actions: list[_Rectangle] = []
    ranks: list[float] = []
    capturing = False
    count: int = 0
    origin: Origin = Origin(0, 0)
    rectangle: pikepdf.Rectangle | None = None

    text = extract_text("test.pdf", page_numbers=[0])
    for l in text.split('\n'):
        if '+' in l:
            print(l)
            print([horse.strip() for horse in l.split('+')])
        if "date prepared" in l.lower():
            dt = l.removeprefix("Date Prepared: ").strip()
            dt = datetime.strptime(dt, "%b %d %Y %I:%M:%S %p")
            print(f"Date Prepared: {dt}")

    with pikepdf.open(file) as pdf:
        page = pdf.pages[0]
        """
        resources = page['/Resources']

        # Find the XObject dictionary
        xobjects = resources['/XObject']

        # Access a specific XObject (e.g., '/X8')
        xobject = xobjects['/X10']
        save_image(xobject, 'test')
        print(f"XObject: {xobject}")

        # Get the width and height
        width = xobject['/Width']
        height = xobject['/Height']

        print(f"Rank Icon Width: {width}, Rank Icon Height: {height}")
        print(f"BoundBox: {page.artbox}")
        """
        for operands, operator in pikepdf.parse_content_stream(page):

            if str(operator) == 'q':
                capturing = True
                continue

            if str(operator) == 'Q':
                if rectangle is None:
                    continue

                actions.append(_Rectangle(str(count), origin, rectangle))

                capturing = False
                rectangle = None
                count += 1
                continue

            if not capturing:
                continue

            match str(operator):
                case 'cm':
                    # print(f"Found Transformation Matrix: {operands}")
                    if len(operands) != 6:
                        print(f"Invalid number (!=6) of operands: {operands}")
                        continue
                    origin = Origin(float(operands[4]), float(operands[5]))
                case 're':
                    # print(f"Found Rectangle: {operands}")
                    if len(operands) != 4:
                        print(f"Invalid number (!=4) of operands: {operands}")
                        continue
                    rectangle = pikepdf.Rectangle(float(operands[0]), float(operands[1]), float(operands[2]), float(operands[3]))
                case 'Do':
                    # print(f"Found XObject Do: {operands}")
                    ranks.append(float(origin.x))
                    continue

                case _:
                    continue

    # FIXME: This is a hack to remove the crown
    ranks.pop(0)

    rects = parse_rectangles(actions)

    attributes: list[Attribute] = []
    for key, value in rects.items():
        attributes.append(Attribute(key, value))

    return attributes, _convert_ranks(_Ranks(*ranks))

def _convert_ranks(ranks: _Ranks) -> list[Rank]:
    return [
        Rank(RankType.D_MINUS, ranks.d-ranks._offset, ranks.d-ranks._offset+ranks._section),
        Rank(RankType.D, ranks.d-ranks._offset+ranks._section, ranks.d-ranks._offset+ranks._section*2),
        Rank(RankType.D_PLUS, ranks.d-ranks._offset+ranks._section*2, ranks.c-ranks._offset),
        Rank(RankType.C_MINUS, ranks.c-ranks._offset, ranks.c-ranks._offset+ranks._section),
        Rank(RankType.C, ranks.c-ranks._offset+ranks._section, ranks.c-ranks._offset+ranks._section*2),
        Rank(RankType.C_PLUS, ranks.c-ranks._offset+ranks._section*2, ranks.b-ranks._offset),
        Rank(RankType.B_MINUS, ranks.b-ranks._offset, ranks.b-ranks._offset+ranks._section),
        Rank(RankType.B, ranks.b-ranks._offset+ranks._section, ranks.b-ranks._offset+ranks._section*2),
        Rank(RankType.B_PLUS, ranks.b-ranks._offset+ranks._section*2, ranks.a-ranks._offset),
        Rank(RankType.A_MINUS, ranks.a-ranks._offset, ranks.a-ranks._offset+ranks._section),
        Rank(RankType.A, ranks.a-ranks._offset+ranks._section, ranks.a-ranks._offset+ranks._section*2),
        Rank(RankType.A_PLUS, ranks.a-ranks._offset+ranks._section*2, ranks.s-ranks._offset),
        Rank(RankType.S_MINUS, ranks.s-ranks._offset, ranks.s-ranks._offset+ranks._section),
        Rank(RankType.S, ranks.s-ranks._offset+ranks._section, ranks.s-ranks._offset+ranks._section*2),
        Rank(RankType.S_PLUS, ranks.s-ranks._offset+ranks._section*2, ranks.ss-ranks._offset),
        Rank(RankType.SS_MINUS, ranks.ss-ranks._offset, ranks.ss-ranks._offset+ranks._section),
        Rank(RankType.SS, ranks.ss-ranks._offset+ranks._section, ranks.ss-ranks._offset+ranks._section*2),
        Rank(RankType.SS_PLUS, ranks.ss-ranks._offset+ranks._section*2, ranks.sss-ranks._offset),
        Rank(RankType.SSS_MINUS, ranks.sss-ranks._offset, ranks.sss-ranks._offset+ranks._section),
        Rank(RankType.SSS, ranks.sss-ranks._offset+ranks._section, ranks.sss-ranks._offset+ranks._section*2),
        Rank(RankType.SSS_PLUS, ranks.sss-ranks._offset+ranks._section*2, ranks.sss-ranks._offset+ranks._section*3)
    ]


def save_image(xobject, filename: str):
    # Extract image properties
    width = xobject['/Width']
    height = xobject['/Height']
    bpc = xobject['/BitsPerComponent']
    filters = xobject.get('/Filter', [])
    
    if not isinstance(filters, list):
        filters = [filters]
    # Extract the raw image data
    raw_data = xobject.read_bytes()

    # Create and save the PPM image
    # PPM header
    header = f'P6 {width} {height} {2**bpc - 1}\n'
    header_bytes = header.encode('ascii')

    # Write the PPM file
    with open(f'{filename}.ppm', 'wb') as f:
        f.write(header_bytes)
        f.write(raw_data)

    print(f"Image {filename}.ppm saved")

attributes, ranks = parse("test.pdf")
pprint(attributes)
pprint(ranks)

pprint(attributes[0].at(attributes[0].values._max_origin+attributes[0].values.maximum, ranks))
pprint(attributes[0].at(attributes[0].values._median_origin+attributes[0].values.median, ranks))
