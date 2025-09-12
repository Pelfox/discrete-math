from collections import Counter
from math import log2
from string import punctuation
from typing import Tuple, Literal


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


def clear_text(text: str) -> str:
    """
    Очищает полученный текст от пробелов и символов препинания.
    :param text: Текст, который требуется очистить.
    :return: Очищенный текст.
    """
    text = text.replace(' ', '')
    for char in punctuation:
        text = text.replace(char, '')
    return text


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


def remove_by_frequency(text: str, mode: Literal['top', 'bottom'], frac: float) -> Tuple[str, set[str]]:
    """
    Удаляет символы из текста по их частоте.
    :param text: Исходный текст для удаления.
    :param mode: Режим удаления: top - наиболее встречаемые; bottom - наименее встречаемые.
    :param frac: Проценталь символов для удаления (например, 0.2).
    :return: Текст без удалённых символов и сами удалённые символы.
    """
    counter = Counter(text)
    if not counter:
        return text, set()

    symbols_count = len(counter)  # мощность алфавита
    remove_n = max(1, round(frac * symbols_count))  # берётся доля символов для удаления из текста

    if mode == 'top':
        to_remove = {char for char, _ in counter.most_common()[:remove_n]}  # удаляем самые частые
    else:
        to_remove = {char for char, _ in counter.most_common()[-remove_n:]}  # удаляем самые редкие

    filtered = ''.join(char for char in text if char not in to_remove)  # строим новую строку без удалённых символов
    return filtered, to_remove


def print_removal_diff(text: str, symbols: set[str], base_entropy: float) -> None:
    """
    Вспомогательная функция для вывода разницы в характеристиках текста после удаления символов.
    :param text: Полученный текст.
    :param symbols: Удалённые символы.
    :param base_entropy: Базовая энтропия исходного текста.
    """
    new_entropy = calculate_entropy(Counter(text))
    print(' * Новый текст:', text)
    print(' * Удалённые символы:', symbols)
    print(' * Энтропия после удаления:', new_entropy)
    print(' * Изменение энтропии:', new_entropy - base_entropy)


def main() -> None:
    with open('Workbook1.txt', 'r', encoding='UTF-8') as file:
        text = file.read()
    print('1) Исходный текст файла:', text)

    text = clear_text(text)
    print('2) Текст после очистки:', text)
    with open('Workbook1_output_1.txt', 'w', encoding='UTF-8') as file:
        file.write(text)

    unigrams = Counter(text)
    bigrams = Counter(text[i:i + 2] for i in range(len(text) - 1))

    print('3) Частота однобуквенных сочетаний:')
    for letter, count in unigrams.items():
        print(f' * {letter}: {count}')

    entropy_unigrams = calculate_entropy(unigrams)
    entropy_bigrams = calculate_entropy(bigrams)
    print('4) Энтропии:')
    print(' * Энтропия для однобуквенных сочетаний:', entropy_unigrams)
    print(' * Энтропия для двухбуквенных сочетаний:', entropy_bigrams)

    code_length, redundancy = calculate_code_length_and_redundancy(unigrams, entropy_unigrams)
    print('5) Длина кода и избыточность:')
    print(' * Длина кода:', code_length)
    print(' * Избыточность:', redundancy)

    text_top_removed, removed_symbols_top = remove_by_frequency(text, 'top', 0.2)
    print('6) После удаления 20% наиболее частых символов:')
    print_removal_diff(text_top_removed, removed_symbols_top, entropy_unigrams)

    text_bottom_removed, removed_symbols_bottom = remove_by_frequency(text, 'bottom', 0.2)
    print('7) После удаления 20% наименее частых символов:')
    print_removal_diff(text_bottom_removed, removed_symbols_bottom, entropy_unigrams)


if __name__ == '__main__':
    main()
