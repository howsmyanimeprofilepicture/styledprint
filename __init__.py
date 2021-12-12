from typing import *
import unicodedata


class StyledPrint:
    def __init__(
        self,
        pattern="bold",
        min_len=0,
        side_ptn=None,
        override_logger=False,
        logging_file_name: str = "logging",
    ):
        if side_ptn is not None:
            assert (
                side_ptn.__len__() == 5
                and type(side_ptn) == tuple
                and type(side_ptn[0]) == str
            )
            for i in range(4):
                self.len(side_ptn[i]) == self.len(side_ptn[i + 1])

        self.min_len: int = min_len
        self.__print = __builtins__["print"]

        self.override_logger: bool = override_logger
        if override_logger:
            import logging

            self.logger = logging.getLogger()
            self.logger.setLevel(logging.INFO)
            # handler 객체 생성
            stream_handler = logging.StreamHandler()
            file_handler = logging.FileHandler(filename=logging_file_name)
            # formatter 객체 생성
            formatter = logging.Formatter(
                fmt="%(message)s \n %(asctime)s - %(name)s - %(levelname)s \n\n"
            )
            # handler에 level 설정
            stream_handler.setLevel(logging.INFO)
            file_handler.setLevel(logging.DEBUG)
            # handler에 format 설정
            stream_handler.setFormatter(formatter)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(stream_handler)
            self.logger.addHandler(file_handler)

        if pattern == "bold":
            self.ptn = "━━"
            self.ptn_side = "┏", "┓", "┗", "┛", "┃"
            self.ptn_len = 2

            return None

        self.ptn: str = pattern
        self.ptn_side = (pattern,) * 5 if side_ptn is None else side_ptn
        self.ptn_len = sum(
            [2 if unicodedata.east_asian_width(char) == "W" else 1 for char in self.ptn]
        )

        return None

    def len(self, text: str) -> int:
        assert type(text) == str
        len_line: int = 0
        for char in text:
            result = unicodedata.east_asian_width(char)
            if result == "W":  # 한글 혹은 이모지란 소리 2칸 차지함
                len_line += 2
            elif (
                result == "Na" or result == "A" or result == "N"
            ):  # 영문, 숫자 등... 1칸 차지하는 녀석들
                len_line += 1
            else:
                self.__print(char, result, "특이 케이스 확인요청")
                len_line += 1
                # raise Exception

        return len_line

    @classmethod
    def use_preset(cls, preset: str, **kargs):
        if preset == "thin":
            return cls(
                pattern="─", min_len=80, side_ptn=("┌", "┐", "└", "┘", "│"), **kargs
            )
        if preset == "bold":
            return cls(min_len=80, **kargs)

        if preset == "heart":
            return cls(
                pattern="♥♡", side_ptn=("♡", "♥", "♡", "♥", "♡"), min_len=80, **kargs
            )

        print(
            """
            Feed right preset into this method please. 
            ex) "thin", "bold", "heart"
            """
        )
        raise Exception

    def __call__(self, *input: str) -> None:
        if type(input) == tuple and len(input) > 1:
            for input_ in input:
                self.__call__(input_)
            return None

        input = input[0]
        if type(input) == dict:
            lines: List[str] = [
                f'\t"{key}" : {value} ,' for key, value in input.items()
            ]
            lines.insert(0, "{")
            lines.append("}")
        elif type(input) == list:
            lines = [f"\t{item}," for item in input]
            lines.insert(0, "[")
            lines.append("]")
        elif type(input) == str:
            lines: List[str] = input.split("\n")
        else:
            input = str(input)
            lines: List[str] = input.split("\n")

        lines = [line.replace("\t", "  ") for line in lines]
        lines = [line.replace("\n", " ") for line in lines]

        # compute the max_length of line in lines
        lengthes = []
        max_length: int = self.min_len
        for line in lines:
            len_line: int = self.len(line)
            lengthes.append(len_line)
            if len_line > max_length:
                max_length = len_line

        while True:
            if max_length % self.ptn_len != 0:
                max_length += 1
                continue
            break

        top_line: str = "\n" + self.ptn_side[0] + (
            self.ptn * (max_length // self.ptn_len)
        ) + self.ptn_side[1]
        bottom_line: str = self.ptn_side[2] + (
            self.ptn * (max_length // self.ptn_len)
        ) + self.ptn_side[3]

        # self.__print(max_length)
        lines = [
            self.ptn_side[4] + line + " " * (max_length - length) + self.ptn_side[4]
            for length, line in zip(lengthes, lines)
        ]

        lines.insert(0, top_line)
        lines.append(bottom_line)

        if self.override_logger:
            self.logger.info("\n".join(lines))

        else:
            self.__print("\n".join(lines))


if __name__ == "__main__":
    pr = StyledPrint.use_preset("thin")
    while 1:
        text = input("💻> ")
        pr(text)
