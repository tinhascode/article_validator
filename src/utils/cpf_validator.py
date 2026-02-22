from __future__ import annotations

import re
from typing import Optional


class CPFValidator:
    def clean(self, value: Optional[str]) -> str:
        if value is None:
            return ""
        return re.sub(r"\D", "", value)

    def is_valid(self, cpf: Optional[str]) -> bool:
        if not cpf:
            return False

        cpf_numbers = self.clean(cpf)

        if len(cpf_numbers) != 11:
            return False

        if cpf_numbers == cpf_numbers[0] * 11:
            return False

        def calc_digit(numbers: str) -> str:
            total = 0
            factor = len(numbers) + 1
            for n in numbers:
                total += int(n) * factor
                factor -= 1
            remainder = total % 11
            digit = 11 - remainder
            if digit >= 10:
                return "0"
            return str(digit)

        first_nine = cpf_numbers[:9]
        d1 = calc_digit(first_nine)
        d2 = calc_digit(first_nine + d1)

        return cpf_numbers.endswith(d1 + d2)

    def format(self, cpf: Optional[str]) -> Optional[str]:
        cleaned = self.clean(cpf)
        if len(cleaned) != 11:
            return None
        return f"{cleaned[0:3]}.{cleaned[3:6]}.{cleaned[6:9]}-{cleaned[9:11]}"


__all__ = ["CPFValidator"]
