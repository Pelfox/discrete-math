from math import log2
from collections import Counter
from typing import Tuple, Optional


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


class Node:
    """Класс, описывающий один узел в алгоритме Хаффмана."""

    def __init__(self, char: str | None, freq: int) -> None:
        self.char = char
        self.freq = freq
        self.right: Node | None = None
        self.left: Node | None = None

    def __lt__(self, other: 'Node') -> bool:
        """Сравнение по частоте (для сортировки узлов)."""
        return self.freq < other.freq

    @staticmethod
    def decode_text(encoded_text: str, tree: "Node") -> list[str]:
        """
        Декодирует двоичную строку, проходя по дереву Хаффмана.
        :param encoded_text: Закодированная строка.
        :param tree: Корень дерева Хаффмана.
        :return: Исходный текст, посимвольно.
        """
        decoded_text = []
        current_node = tree
        for bit in encoded_text:
            if bit == "1":
                current_node = current_node.left
            else:
                current_node = current_node.right
            # дошли до листа в корне - символ для декодирования найден
            if current_node and current_node.char:
                decoded_text.append(current_node.char)
                current_node = tree  # возвращаемся к корню
        return decoded_text

    @staticmethod
    def build_huffman_codes(chars: list[str], counter: Counter) -> Tuple[dict[str, str], str, Optional["Node"]]:
        """
        Строит дерево Хаффмана по символам и их частотам.
        :param chars: Список элементов (символов или биграмм) исходного текста.
        :param counter: Счётчик частот этих элементов.
        :return: (кодек, закодированная строка, дерево Хаффмана).
        """
        nodes = [Node(char, freq) for char, freq in counter.items()]
        # пока узлов больше одного — объединяем два наименее частых
        while len(nodes) > 1:
            # находим два узла с минимальными значениями частоты
            nodes.sort(key=lambda x: x.freq)
            left = nodes.pop(0)
            right = nodes.pop(0)

            # создаём новый узел на основе найденных предыдущих
            merged = Node(None, left.freq + right.freq)
            merged.left = left
            merged.right = right
            nodes.append(merged)

        # рекурсивно обходим дерево и формируем коды
        huffman_codes = {}
        def generate_codes(node: Node | None, code: str = "") -> None:
            if node is None:
                return
            if node.char is not None:
                huffman_codes[node.char] = code or "0"
            # генерируем коды для правого поддерева
            generate_codes(node.right, code + "0")
            # генерируем коды для левого поддерева
            generate_codes(node.left, code + "1")
        generate_codes(nodes[0])

        # закодированный текст = конкатенация кодов символов
        return huffman_codes, "".join(huffman_codes[char] for char in chars), nodes[0]


def calculate_avg_length(text: str, codec: dict[str, str], counter: Counter) -> float:
    """
    Считает среднюю длину кодового слова по распределению частот.
    :param text: Исходный текст (для подсчёта общего числа символов).
    :param codec: Кодек, полученный из кодирования алгоритмом Хаффмана.
    :param counter: Счётчик символов.
    :return: Средняя длина кода (бит/символ).
    """
    avg_length = 0.0
    total_length = len(text)
    for char, code in codec.items():
        probability = counter[char] / total_length
        avg_length += probability * len(code)
    return avg_length


def join_bigrams(bigrams: list[str]) -> str:
    """
    Восстанавливает исходный текст из последовательности биграмм.
    :param bigrams: Список строк-двоек (биграмм), полученных при декодировании.
    :return: Восстановленный исходный текст.
    """
    if not bigrams:
        return ""
    result = [bigrams[0]]  # первый биграмм целиком
    result.extend(bigram[-1] for bigram in bigrams[1:])  # из остальных только последний символ
    return "".join(result)


def main() -> None:
    with open('Workbook3.txt', 'r', encoding='utf-8') as file:
        text = file.read()

    counter = Counter(text)
    print('1) Статистическая обработка:')
    for char, freq in sorted(counter.items()):
        print(f' * {char}: {freq}')

    print('2) Энтропия, длина при равномерном кодировании и избыточность:')
    entropy = calculate_entropy(counter)
    code_length, redundancy = calculate_code_length_and_redundancy(counter, entropy)
    print(f' * Длина при равномерном кодировании: {code_length:.2f}')
    print(f' * Избыточность длины: {redundancy:.2f}')

    print('3) Построение дерева Хаффмана (однобуквенные):')
    codes, encoded, tree = Node.build_huffman_codes(list(text), counter)
    decoded = "".join(Node.decode_text(encoded, tree))
    avg_length = calculate_avg_length(text, codes, counter)
    efficiency = entropy / avg_length
    print(f' * Коды Хаффмана:')
    for char, code in codes.items():
        print(f'  * {char}: {code}')
    print(f' * Закодированный текст: {encoded}')
    print(f' * Декодированный текст: {decoded} (совпадает? {decoded == text})')
    print(f' * Средняя длина элементарного кода: {avg_length}')
    print(f' * Эффективность кодирования: {efficiency:.2f} ({efficiency * 100:.2f}%)')

    print('4) Построение дерева Хаффмана (двухбуквенные):')
    bigrams = [text[i:i + 2] for i in range(len(text) - 1)]
    bigrams_counter = Counter(bigrams)
    bigrams_codes, bigrams_encoded, bigrams_tree = Node.build_huffman_codes(bigrams, bigrams_counter)
    bigrams_decoded = join_bigrams(Node.decode_text(bigrams_encoded, bigrams_tree))

    # Средняя длина кода на символ (нужно делить на 2, т.к. биграмма = 2 символа)
    bigrams_avg_length = calculate_avg_length(text, bigrams_codes, bigrams_counter)
    bigrams_efficiency = calculate_entropy(bigrams_counter) / (
        sum(freq * len(bigrams_codes[bg]) for bg, freq in bigrams_counter.items()) / sum(bigrams_counter.values())
    )

    print(f' * Коды Хаффмана:')
    print(calculate_entropy(bigrams_counter))
    for char, code in bigrams_codes.items():
        print(f'  * {char}: {code}')
    print(f' * Закодированный текст: {bigrams_encoded}')
    print(f' * Декодированный текст: {bigrams_decoded} (совпадает? {bigrams_decoded == text})')
    print(f' * Средняя длина элементарного кода: {bigrams_avg_length}')
    print(f' * Эффективность кодирования: {bigrams_efficiency:.2f} ({bigrams_efficiency * 100:.2f}%)')


if __name__ == '__main__':
    main()
