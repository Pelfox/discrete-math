from collections import Counter
from math import log2
from typing import Tuple


def calculate_entropy(counter: Counter) -> float:
    """
    Подсчитывает энтропию текста по формуле Шеннона.
    :param counter: Счётчик символов из текста.
    :return: Энтропия исходного текста по формуле Шеннона.
    """
    n = sum(counter.values())
    if n == 0:  # единичный случай: все символы текста идентичны
        return 0.0
    return sum((c / n) * log2(1 / (c / n)) for c in counter.values())


def calculate_code_length_and_redundancy(counter: Counter, entropy: float) -> Tuple[float, float]:
    """
    Подсчитывает минимальную длину и её избыточность кода для равномерного побуквенного кодирования текста.
    :param counter: Счётчик символов исходного текста.
    :param entropy: Энтропия исходного текста.
    :return: Минимальная длина кодирования и её избыточность.
    """
    symbols_count = len(counter)
    # единичный случай: все символы текста идентичны
    if symbols_count <= 1:
        return 0.0, 0.0
    code_length = log2(symbols_count)
    return code_length, 1 - entropy / code_length  # избыточность кода


def calculate_shannon_fano(counter: Counter) -> dict[str, str]:
    """
    Данная функция строит словарь для текста по алгоритму Шеннона-Фано.
    :param counter: Счётчик символов исходного текста.
    :return: Словарь, где ключ - символ, а значение - его код.
    """
    # составляем словарь из символов текста и их кодов (в будущем)
    codes = {char: '' for char in counter}

    def split(group):
        # если в группе 1 символ, делить нечего
        if len(group) <= 1:
            return

        total = sum(frequency for _, frequency in group)  # подсчитываем общее количество символов в тексте
        acc = 0  # "накопитель" частот слева направо
        cut_idx = 0  # текущий индекс разреза
        for i, (_, frequency) in enumerate(group):
            acc += frequency
            if acc >= total / 2:  # если больше половины, то режем после неё
                cut_idx = i + 1
                break

        left, right = group[:cut_idx], group[cut_idx:]
        # по алгоритму Шеннона-Фано: добавляем 0 к кодам слева, а 1 - справа
        for char, _ in left:
            codes[char] += '0'
        for char, _ in right:
            codes[char] += '1'

        split(right)
        split(left)

    # сортируем частоту символов по убыванию
    split(sorted(counter.items(), key=lambda x: x[1], reverse=True))
    return codes


def encode(text: list[str], codec: dict[str, str]) -> str:
    """
    Кодирует приведённый текст при помощи ранее полученных кодов.
    :param text: Текст, который требуется закодировать.
    :param codec: Кодек - набор кодов для кодирования текста.
    :return: Закодированный текст, или же ошибка, если какие-то символы невозможно закодировать.
    """
    missing = {char for char in set(text) if char not in codec}
    if missing:
        raise ValueError(f'Missing characters: {missing}')
    return ''.join(codec[char] for char in text)


def decode(bitstring: str, codec: dict[str, str]) -> str:
    """
    Декодирует строковый набор битов в текст при помощи кодека.
    :param bitstring: Строковый набор битов для декодирования.
    :param codec: Кодек, использовавшийся для кодирования текста.
    :return: Декодированный текст.
    """
    result, buffer = [], ''
    reversed_codec = {code: char for char, code in codec.items()}
    for char in bitstring:
        buffer += char
        if buffer in reversed_codec:
            result.append(reversed_codec[buffer])
            buffer = ''
    return ''.join(result)


def avg_code_length(codec: dict[str, str], counter: Counter) -> float:
    """
    Подсчитывает среднюю длину для символа по формуле из лекции.
    :param codec: Кодек для кодирования/декодирования текста.
    :param counter: Счётчик символов исходного текста.
    :return: Средняя длина символа кодировки.
    """
    char_counts = sum(counter.values())
    # случай, если все символы в тексте идентичные
    if char_counts == 0:
        return 0.0
    return sum((counter[char] / char_counts) * len(code) for char, code in codec.items())

def main() -> None:
    with open("Workbook2.txt") as file:
        text = file.read()
    print('1) Исходный текст:', text)

    unigrams = Counter(text)
    bigrams = Counter(text[i:i + 2] for i in range(len(text) - 1))

    entropy = calculate_entropy(unigrams)
    code_length, redundancy = calculate_code_length_and_redundancy(unigrams, entropy)
    print('2) Энтропия, длина кода и избыточность:')
    print(' * Энтропия исходного текста:', entropy)
    print(' * Длина кода:', code_length)
    print(' * Избыточность кода:', redundancy)

    shannon_fano = calculate_shannon_fano(unigrams)
    print('3) Схема алфавитного кодирования текста по Шеннону-Фано:')
    for char, code in shannon_fano.items():
        print(f' * {char}: {code}')

    encoded = encode(list(text), shannon_fano)
    decoded = decode(encoded, shannon_fano)
    avg_length = avg_code_length(shannon_fano, unigrams)
    efficiency = entropy / avg_length
    print('4) Свойства закодированного текста и его декодирование:')
    print(' * Закодированный текст:', encoded)
    print(' * Декодированный текст:', decoded)
    print(' * Совпадает ли декодированный текст с исходным?', decoded == text)
    print(' * Средняя длина символа кодировки:', avg_length)
    print(' * Эффективность кодирования:', efficiency, f'({efficiency * 100}%)')

    bigrams_entropy = calculate_entropy(bigrams)
    bigrams_codec = calculate_shannon_fano(bigrams)
    bigrams_avg_length = avg_code_length(bigrams_codec, bigrams)
    bigrams_efficiency = entropy / bigrams_avg_length

    bigrams_encoded = encode([text[i:i+2] for i in range(len(text)-1)], bigrams_codec)
    bigrams_decoded = decode(bigrams_encoded, bigrams_codec)

    print('5) Расчёты для двухбуквенных комбинаций:')
    print(' * Энтропия:', bigrams_entropy)
    print(' * Средняя длина символа кодировки:', bigrams_avg_length)
    print(' * Эффективность кодирования:', bigrams_efficiency, f'({bigrams_efficiency * 100}%)')
    print(' * Схема кодирования по Шеннону-Фено:')
    for char, code in bigrams_codec.items():
        print(f'  * {char}: {code}')
    print(' * Закодированный текст:', bigrams_encoded)
    print(' * Декодированный текст (наложение биграм):', bigrams_decoded)


if __name__ == "__main__":
    main()
