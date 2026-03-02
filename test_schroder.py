def count_unadjusted_paths(max_n):
    memo = {}
    
    def count_paths(a, c, b, d):
        if a==0 and c==0 and b==0 and d==0:
            return 1
            
        state = (a, c, b, d)
        if state in memo:
            return memo[state]
            
        ways = 0
        if a>=1 and b>=1:
            ways += count_paths(a-1, c+1, b-1, d+1)
        if c>=1 and b>=1:
            ways += count_paths(a, c-1, b-1, d+1)
        if a>=1 and d>=1:
            ways += count_paths(a-1, c+1, b, d-1)
            
        memo[state] = ways
        return ways
        
    seq = []
    for n in range(1, max_n + 1):
        seq.append(count_paths(n, 0, n, 0))
        
    return seq

def generate_adjusted_path_counts(max_n):
    memo = {}
    
    def adjust(a, c, b, d):
        c = min(c, b)
        d = min(d, a)
        return (a, c, b, d)
        
    def count_paths(a, c, b, d):
        if a==0 and c==0 and b==0 and d==0:
            return 1
            
        state = (a, c, b, d)
        if state in memo:
            return memo[state]
            
        ways = 0
        if a>=1 and b>=1:
            na, nc, nb, nd = adjust(a-1, c+1, b-1, d+1)
            ways += count_paths(na, nc, nb, nd)
        if c>=1 and b>=1:
            na, nc, nb, nd = adjust(a, c-1, b-1, d+1)
            ways += count_paths(na, nc, nb, nd)
        if a>=1 and d>=1:
            na, nc, nb, nd = adjust(a-1, c+1, b, d-1)
            ways += count_paths(na, nc, nb, nd)
            
        memo[state] = ways
        return ways
        
    seq = []
    for n in range(1, max_n + 1):
        a, c, b, d = adjust(n, 0, n, 0)
        seq.append(count_paths(a, c, b, d))
        
    return seq

n_val = 10
unadjusted = count_unadjusted_paths(n_val)
adjusted = generate_adjusted_path_counts(n_val)

print("Adjusted (DoubleChess):", adjusted)
print("Unadjusted (Hypothesis):", unadjusted)

diff = [adj - unadj for adj, unadj in zip(adjusted, unadjusted)]
print("Difference (Adjusted - Unadjusted):", diff)

# Known Little Schröder sequence shifted or not:
# A001003: 1, 1, 3, 11, 45, 197, 903, 4279, 20793, 103049, 518859
ls = [1, 3, 11, 45, 197, 903, 4279, 20793, 103049, 518859]
print("Little Schroder (n>=2): ", ls[:n_val])
MATCH = (unadjusted == ls[:n_val])
print("Unadjusted exactly matches Little Schroder? ", MATCH)
