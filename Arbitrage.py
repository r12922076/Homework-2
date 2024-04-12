liquidity = {
    ("tokenA", "tokenB"): (17, 10),
    ("tokenA", "tokenC"): (11, 7),
    ("tokenA", "tokenD"): (15, 9),
    ("tokenA", "tokenE"): (21, 5),
    ("tokenB", "tokenC"): (36, 4),
    ("tokenB", "tokenD"): (13, 6),
    ("tokenB", "tokenE"): (25, 3),
    ("tokenC", "tokenD"): (30, 12),
    ("tokenC", "tokenE"): (10, 8),
    ("tokenD", "tokenE"): (60, 25),
}

def getAmountOut(amountIn, reserveIn, reserveOut):
    assert amountIn > 0, 'UniswapV2Library: INSUFFICIENT_INPUT_AMOUNT'
    assert reserveIn > 0 and reserveOut > 0, 'UniswapV2Library: INSUFFICIENT_LIQUIDITY'
    amountInWithFee = amountIn * 997
    numerator = amountInWithFee * reserveOut
    denominator = reserveIn * 1000 + amountInWithFee
    amountOut = numerator / denominator
    return amountOut

def cal_token(tokenIn, tokenOut, num_token):
    # Check if the pair (tokenIn, tokenOut) is in the liquidity dictionary
    if (tokenIn, tokenOut) in liquidity:
        # Access the reserves for the tokenIn to tokenOut direction
        liquidity_data = liquidity[(tokenIn, tokenOut)]
        (reserveIn, reserveOut) = liquidity_data
    else:
        # Access the reserves for the tokenOut to tokenIn direction if the direct pair doesn't exist
        liquidity_data = liquidity[(tokenOut, tokenIn)]
        (reserveOut, reserveIn) = liquidity_data
    # Calculate and return the amount of tokenOut that can be obtained for num_token of tokenIn
    return getAmountOut(num_token, reserveIn, reserveOut)


# path = ["tokenB", "tokenA", "tokenD", "tokenB"]
# path: tokenB->tokenA->tokenD->tokenB, tokenB balance=3.770765

def cal_path_token(path):
    # Initialize the number of tokens to be used in the first exchange
    num_token = 5
    
    # Iterate through the path list from the first token to the second-last token
    for i in range(len(path)-1):
        # Set the current token as tokenIn and the next token in the list as tokenOut
        tokenIn = path[i]
        tokenOut = path[i+1]
        
        # Calculate the resulting number of tokens after swapping from tokenIn to tokenOut
        num_token = cal_token(tokenIn, tokenOut, num_token)
    
    # Return the number of tokens left after completing all swaps in the path
    return num_token

def my_print(token_path, num_token):
    # Convert the path list to a string in the specified format
    path_str = "->".join(token_path)

    # Format the final balance and convert it to a string, keeping six decimal places
    balance_str = f"{num_token:.6f}"  # Retain six decimal places

    # Combine the two parts together
    output_str = f"path: {path_str}, tokenB balance={balance_str}"

    # Print the result
    print(output_str)

def generate_paths(s):
    def backtrack(path, options):
        if path not in result and len(path) >= 2:  # Avoid duplicate permutations
            internal_tokens = [f"token{char}" for char in path]
            token_path = ["tokenB"] + internal_tokens + ["tokenB"]
            num_token = cal_path_token(token_path)
            if num_token >= 20:
                my_print(token_path, num_token)
                return True
            result.append(path)
        
        for i in range(len(options)):
            if backtrack(path + options[i], options[:i] + options[i+1:]):
                return True
    
    result = []
    backtrack("", s)
    return

generate_paths("ACDE")