import string
from collections import defaultdict, deque


class Grammar:
    def __init__(self):
        self.rules = defaultdict(list)
        self.epsilon_left_part = set()
        self.new_epsilon_left_part = set()
        self.used_symbols = [False] * 26
        self.used_terminals = [''] * 26
        self.first_available_symbol = 0

    def add_rule(self, rule):
        left_part = rule[0]
        right_part = rule[3:]
        self.used_symbols[ord(left_part) - ord('A')] = True
        if right_part == "e":
            self.epsilon_left_part.add(left_part)
        else:
            self.rules[left_part].append(right_part)

    def is_terminal(self, symbol):
        return symbol.islower()

    def insert_rule(self, left_part, right_part):
        self.rules[left_part].append(right_part)

    def delete_long_rules(self):
        queue = deque()
        for left, productions in list(self.rules.items()):
            for production in productions:
                if len(production) > 2:
                    while self.used_symbols[self.first_available_symbol]:
                        self.first_available_symbol += 1
                    new_symbol = chr(self.first_available_symbol + ord('A'))
                    self.used_symbols[self.first_available_symbol] = True
                    queue.append((new_symbol, production[1:]))
                    self.rules[left].remove(production)
                    self.rules[left].append(production[0] + new_symbol)

        while queue:
            left_part, right_part = queue.popleft()
            if len(right_part) > 2:
                while self.used_symbols[self.first_available_symbol]:
                    self.first_available_symbol += 1
                new_symbol = chr(self.first_available_symbol + ord('A'))
                self.used_symbols[self.first_available_symbol] = True
                queue.append((new_symbol, right_part[1:]))
                self.rules[left_part].append(right_part[0] + new_symbol)
            else:
                self.rules[left_part].append(right_part)

    def find_epsilon(self):
        changed = True
        while changed:
            changed = False
            for left, productions in self.rules.items():
                if left in self.epsilon_left_part:
                    continue
                for production in productions:
                    if all(symbol in self.epsilon_left_part for symbol in production):
                        self.epsilon_left_part.add(left)
                        changed = True
                        break

    def delete_epsilon(self):
        self.find_epsilon()
        for left, productions in list(self.rules.items()):
            new_productions = []
            for production in productions:
                subsets = self._generate_subsets(production)
                for subset in subsets:
                    if subset and subset not in productions:
                        new_productions.append(subset)
            self.rules[left].extend(new_productions)

    def _generate_subsets(self, string):
        if not string:
            return [""]
        rest = self._generate_subsets(string[1:])
        return [string[0] + s for s in rest] + rest

    def delete_chain_rules(self):
        for left in list(self.rules.keys()):
            self._resolve_chain_rules(left)

    def _resolve_chain_rules(self, symbol):
        queue = deque([symbol])
        seen = set(queue)
        while queue:
            current = queue.popleft()
            for production in list(self.rules[current]):
                if len(production) == 1 and production.isupper():
                    if production not in seen:
                        queue.append(production)
                        seen.add(production)
                    self.rules[current].remove(production)
                    self.rules[current].extend(self.rules[production])

    def delete_multiple_terminals(self):
        for left, productions in list(self.rules.items()):
            for production in productions:
                if len(production) == 2 and (self.is_terminal(production[0]) or self.is_terminal(production[1])):
                    for i, char in enumerate(production):
                        if self.is_terminal(char):
                            index = ord(char) - ord('a')
                            if not self.used_terminals[index]:
                                while self.used_symbols[self.first_available_symbol]:
                                    self.first_available_symbol += 1
                                new_symbol = chr(self.first_available_symbol + ord('A'))
                                self.used_symbols[self.first_available_symbol] = True
                                self.used_terminals[index] = new_symbol
                                self.rules[new_symbol].append(char)
                            production = production[:i] + self.used_terminals[index] + production[i + 1:]
                            self.rules[left].remove(production)
                            self.rules[left].append(production)

    def to_chomsky(self):
        self.delete_long_rules()
        self.delete_epsilon()
        self.delete_chain_rules()
        self.delete_multiple_terminals()


class CYKParser:
    def __init__(self, grammar):
        self.grammar = grammar

    def parse(self, word):
        n = len(word)
        dp = defaultdict(lambda: [[False] * n for _ in range(n)])
        for i, char in enumerate(word):
            for left, productions in self.grammar.rules.items():
                for production in productions:
                    if production == char:
                        dp[left][i][i] = True

        for length in range(2, n + 1):
            for i in range(n - length + 1):
                j = i + length - 1
                for k in range(i, j):
                    for left, productions in self.grammar.rules.items():
                        for production in productions:
                            if len(production) == 2:
                                A, B = production
                                if dp[A][i][k] and dp[B][k + 1][j]:
                                    dp[left][i][j] = True

        return dp['S'][0][n - 1]  


def main():
    grammar = Grammar()
    quantity_rules = int(input())
    quantity_words = int(input())

    for _ in range(quantity_rules):
        rule = input().strip()
        grammar.add_rule(rule)

    grammar.to_chomsky()
    parser = CYKParser(grammar)

    for _ in range(quantity_words):
        word = input().strip()
        print("YES" if parser.parse(word) else "NO")


if __name__ == "__main__":
    main()

'''
3
2
S->AB
A->a
B->b
ab
ba
______
YES
NO
'''
