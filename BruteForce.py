import sys
import time

min_support = float(sys.argv[1])
min_confidence = float(sys.argv[2])
transaction_file = sys.argv[3]

with open(transaction_file) as fp:
    dataset = [f.replace("\n", "").strip().split(",") for f in fp]

flatlist = [item for sublist in dataset for item in sublist]
data = list(set(flatlist))


def get_combinations(output, req_len, current_lst=[], idx=0):
    if len(current_lst) == req_len:
        output.append(current_lst)
        return

    if idx >= len(data):
        return

    get_combinations(output, req_len, current_lst + [data[idx]], idx + 1)
    get_combinations(output, req_len, current_lst, idx + 1)


def find_count_set(db, s):
    count = 0
    for t in db:
        if s.issubset(t):
            count += 1
    return count


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


def rules_helper(itemset, support_values, rules):
    for item in itemset:    # Get a single item
        single_set = frozenset([item])
        rem_items = itemset - single_set

        confidence = support_values[itemset] / support_values[single_set]
        if confidence >= min_confidence:
            rules.append([single_set, rem_items, confidence])

        confidence = support_values[itemset] / support_values[rem_items]
        if confidence >= min_confidence:
            rules.append([rem_items, single_set, confidence])

        if len(rem_items) > 1:
            rules_helper(rem_items, support_values, rules)


def create_association_rules(freq_itemsets, support_values):
    rules = []

    for itemset in freq_itemsets:
        rules_helper(itemset, support_values, rules)

    # Deduplicate rules
    rule_hashes = set()
    final_rules = []
    for rule in rules:
        rule_hash = '|'.join(rule[0]) + '||' + '|'.join(rule[1])
        if rule_hash not in rule_hashes:
            final_rules.append(rule)
        rule_hashes.add(rule_hash)

    return final_rules


def format_rules(rules):
    return [','.join(left) + ' ' + '\u2192' + ' ' + ','.join(right) + " [Confidence=" + str(confidence) + "]" for
            [left, right, confidence] in rules]


def create_freq_itemset_support_bruteforce():
    frequent = []
    all_supports = {}
    support_values = {}

    for i in range(1, len(data) + 1):
        all_combinations = []
        get_combinations(all_combinations, i)

        for comb in all_combinations:
            comb_set = frozenset(comb)
            if comb_set in all_supports:
                support = all_supports[comb_set]
            else:
                count = find_count_set(dataset, comb_set)
                support = count / len(dataset)
                all_supports[comb_set] = support

            if support >= min_support:
                support_values[comb_set] = support
                if len(comb_set) > 1:
                    frequent.append(comb_set)

    return frequent, support_values


def main():
    start_time = time.time()
    f, s = create_freq_itemset_support_bruteforce()
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