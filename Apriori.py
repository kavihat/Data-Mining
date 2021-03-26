import sys
import time

# User inputted support and confidence values
min_support = float(sys.argv[1])
min_confidence = float(sys.argv[2])
dataset = sys.argv[3]

# Reading the transactions in dataset to a list named data
with open(dataset) as fp:
    data = [f.replace("\n", "").strip().split(",") for f in fp]


def create_freq_itemset_support_apriori():
    supportdct = {}
    candidate = []
    large_itemset = []
    initial_candidates = set()
    for i in data:
        for j in i:
            initial_candidates.add(frozenset([j]))

    candidate.append(initial_candidates)
    cs = {st: 0 for st in initial_candidates}
    for d in data:
        for frequent_set in initial_candidates:
            if frequent_set.issubset(d):
                cs[frequent_set] += 1
    transaction_size = len(dataset)

    calculate_support = {freqset: support / transaction_size for freqset, support in cs.items() if
                         support / transaction_size >= min_support}
    large_itemset.append(list(calculate_support.keys()))
    supportdct.update(calculate_support)
    step = 0
    while len(large_itemset[step]) > 1:
        candidate = create_candidate(large_itemset[step])
        cs = {st: 0 for st in candidate}
        for d in data:
            for frequent_set in candidate:
                if frequent_set.issubset(d):
                    cs[frequent_set] += 1

        calculate_support = {freqset: support / transaction_size for freqset, support in cs.items() if
                             support / transaction_size >= min_support}

        supportdct.update(calculate_support)
        if len(calculate_support) == 0:
            break
        large_itemset.append(list(calculate_support.keys()))
        step += 1

    return large_itemset, supportdct


def create_candidate(large_item_set):
    result = []
    for i in range(len(large_item_set)):
        for j in range(i + 1, len(large_item_set)):
            a, b = large_item_set[i], large_item_set[j]
            aa, bb = list(a), list(b)
            aa.sort()
            bb.sort()
            if aa[:len(a) - 1] == bb[:len(a) - 1]:
                result.append(a | b)

    return result


def get_rule_hash(rule):
    """Expected to be of the form: [frozenset({left}), frozenset({right}), <confidence> (optional)]"""
    return '|'.join(list(rule[0])) + '||' + '|'.join(list(rule[1]))


def get_permutations(output, head, tail=[]):
    if len(head) == 0:
        output.append(tail)
    else:
        for i in range(len(head)):
            get_permutations(output, head[:i] + head[i + 1:], tail + [head[i]])


def create_association_rules(freq_itemsets, support_values):
    rules = {}

    for itemsets in freq_itemsets[1:]:
        for itemset in itemsets:
            item_permutations = []
            get_permutations(item_permutations, list(itemset))
            for permutation in item_permutations:
                permutation_set = frozenset(permutation)
                for i in range(1, len(permutation)):
                    left = frozenset(permutation[:i])
                    right = permutation_set - left

                    rule_hash = get_rule_hash([left, right])
                    if rule_hash not in rules:
                        confidence = support_values[itemset] / support_values[left]
                        if confidence >= min_confidence:
                            rules[rule_hash] = [left, right, confidence]
                        else:
                            rules[rule_hash] = None

    final_rules = []
    for rule_hash, rule in rules.items():
        if rule:
            final_rules.append(rule)

    return final_rules


def format_rules(rules):
    return [','.join(left) + ' ' + '\u2192' + ' ' + ','.join(right) + " [Confidence=" + str(confidence) + "]" for
            [left, right, confidence] in rules]


def main():
    start_time = time.time()
    f, s = create_freq_itemset_support_apriori()
    assoc_rules = create_association_rules(f, s)
    assoc_rules = format_rules(assoc_rules)
    end_time = time.time()

    print("{} rules generated".format(len(assoc_rules)))
    print("\nAssociation Rules and their confidence values :\n")
    for rule in assoc_rules:
        print(rule)
    print("\nRunning Time", str(end_time - start_time) + 's')


if __name__ == '__main__':
    main()