# 2024-Spring-HW2

Please complete the report problem below:

## Problem 1
Provide your profitable path, the amountIn, amountOut value for each swap, and your final reward (your tokenB balance).

> Solution:
> 
> path: tokenB->tokenA->tokenD->tokenC->tokenB
> - tokenB->tokenA: (amountIn, amountOut) = (5000000000000000000 wei, 5655321988655321988 wei)
> - tokenA->tokenD: (amountIn, amountOut) = (5655321988655321988 wei, 2458781317097933552 wei)
> - tokenD->tokenC: (amountIn, amountOut) = (2458781317097933552 wei, 5088927293301515695 wei)
> - tokenC->tokenB: (amountIn, amountOut) = (5088927293301515695 wei, 20129888944077446732 wei)
> 
> tokenB balance=20.129889
> 
> Ref: Traces from forge test [5000000000000000000 [5e18], 5655321988655321988 [5.655e18], 2458781317097933552 [2.458e18], 5088927293301515695 [5.088e18], 20129888944077446732 [2.012e19]]

## Problem 2
What is slippage in AMM, and how does Uniswap V2 address this issue? Please illustrate with a function as an example.

> Solution:
> 
> 滑點 (slippage) 是指交易執行的價格與預期的價格之間的差異，是我們在自動化做市商 (AMM) 平台如 Uniswap V2 會遇到的風險。這種價格差異發生的原因是買賣雙方資產供需的變化，進而影響資產價格，其中，對於 AMM 來說，價格常是根據兩種交換資產的相對供應量，再通過數學公式來計算的，而若是存在其他大型交易發生，那可能會顯著改變資產供應的比率，從而影響到價格，導致滑點。
> 
> Uniswap V2 可通過使用者設定至少要獲得多少代幣，以避免滑點造成比預期大的損失，以下是交換代幣時可用的 function 之ㄧ：
> ```
> function swapExactTokensForTokens(
>  uint amountIn,
>  uint amountOutMin,
>  address[] calldata path,
>  address to,
>  uint deadline
> ) external returns (uint[] memory amounts);
> ```
> 以此作業為例，我們可以將 amountOutMin 設為 20，那麼就可以避免滑點造成收到的代幣小於 20，即如 
> ```
> router.swapExactTokensForTokens(5 ether, 20 ether, path, arbitrager, block.timestamp + 300);
> ```

## Problem 3
Please examine the mint function in the UniswapV2Pair contract. Upon initial liquidity minting, a minimum liquidity is subtracted. What is the rationale behind this design?

> Solution:
> 
> 在 UniswapV2Pair 的合約中的 mint 用於添加流動性，而當 totalSupply = 0 時，此為第一次建立代幣池的流動性，Uniswap V2 會扣除一個特定的最小流動性量，在程式中以 MINIMUM_LIQUIDITY 表示，其設定的值為 1,000，此部分流動性被永久鎖定在池中。
> 
> 扣除 MINIMUM_LIQUIDITY 會有幾個好處：
> 1. **防止代幣池為零**：通過永久鎖定少量的流動性，Uniswap 可以確保此池永遠不會因為 swap 導致代幣完全被耗盡，此在代幣池的初始階段非常特別重要，是因為可以避免起初代幣不多時，因為計算時的四捨五入導致代幣的計算錯誤。
> 2. **避免除以零的情況**：在 Uniswap V2 公式中，流動性代幣的相對價值是根據該兩代幣池中資產的比率所計算出的，此過程中會除上代幣的數量，而若是池中的流動性變為零，就可能會導致除以零的錯誤。
> 3. **表示池已初始化的象徵值**：MINIMUM_LIQUIDITY 可以充當該代幣池已被初始化的標記。
> 4. **安全原因**：通過永久鎖定少量流動性，代幣池將永遠無法完全耗盡，此有助於阻止某些類型的操縱或惡意的攻擊行為。
> 
> Ref: https://github.com/Uniswap/v2-core/blob/master/contracts/UniswapV2Pair.sol

## Problem 4
Investigate the minting function in the UniswapV2Pair contract. When depositing tokens (not for the first time), liquidity can only be obtained using a specific formula. What is the intention behind this?

> Solution:
> 
> 在向 Uniswap V2 的現有池中添加流動性時，流動性代幣（LP 代幣）給存款人的發行數量是通過一公式來決定的，目的是讓 LP 代幣 的發行對每位參與者都是公平的，方法是讓 LP 代幣的發行數量與其對池的貢獻成比例。
> 
> 在非第一次進行 depositing tokens 時，LP 代幣的計算是如以下的程式（擷取自UniswapV2Pair 的合約中）
> ```language=solidity
> liquidity = Math.min(amount0.mul(_totalSupply)/_reserve0, amount1.mul(_totalSupply) / _reserve1);
> ```
> 如果我們將其寫成數學式子，會像是
> $$L = \min\left(\frac{A}{A_{\text{res}}} \cdot L_{\text{total}}, \frac{B}{B_{\text{res}}} \cdot L_{\text{total}}\right)$$
> 其中 $A_{\text{res}}$ 和 $B_{\text{res}}$ 是原本池中代幣 A 和 B 的儲備量，而 $L_{\text{total}}$ 則是原本 LP 代幣的總供應量。
> 
> 這種設計會有幾個好處，分別是
> 1. **比例所有權**：此公式可確保發行的 LP 代幣量與存款人添加的流動性相比於當前池大小的比例成比例，可維持所有權分配的公平性，以確保存款人在池中的份額準確反映其貢獻。
> 2. **價值保護**：由於是透過基於對現有池相對大小的存款來發行新的 LP 代幣，此可確保新增的流動性不會稀釋現有 LP 代幣的價值，來保護所有流動性提供者份額的價值。
> 3. **鼓勵平衡存款**：公式中使用 min 函數來計算，其可鼓勵流動性提供者按照當前池的比率來存入兩種代幣，這使得池會較為平衡和穩定。

## Problem 5
What is a sandwich attack, and how might it impact you when initiating a swap?

> Solution:
> 
> 三明治攻擊是一種在使用 AMM 的 Defi 交易所上可能可以觀察到的操縱行為，其是針對的是正在發起代幣交換的用戶進行攻擊，導致該用戶得到的兌換率比原先隨機的情況差。
> 
> 三明治攻擊的工作原理可分為 4 步：
> 1. **識別**：攻擊者識別到某個用戶發起的交易，該交易是打算將大量的某種代幣換成另一種，但該交易尚未由區塊鏈網路確認，而由於該網路的公開性，所有參與者其實都可以看的到待處理的交易。
> 2. **前置交易**：攻擊者可以更高的礦工費發起交易，來確保該交易在用戶的交易前被確認，而在攻擊者的交易中，攻擊者會購買用戶打算購買的同一代幣，此時會由於該代幣的需求增加，而使其價格上漲。
> 3. **用戶的交易**：此時用戶的原始交易被確認了，但是是以現在增加的價格購買代幣，導致用戶以比預期更高的價格交換代幣，因此獲得代幣的較少。
> 4. **後置交易**：最後，因為代幣的價格因為被攻擊者的購買而再次上升，此時攻擊者可通過賣出他們最初購買的代幣來完成三明治攻擊，從而由被攻擊者的交易所創造的價格差異中獲利。
> 
> 因此，若我們進行 swap 時被三明治攻擊，會受到一些負面影響如
> - **較差的代幣交換率**：因為交易會在無意中被提高代幣價格，而獲得比預期更少的代幣。
> - **財務損失**：既然獲得的代幣較少，就表直接的財務損失。
> - **市場影響**：三明治攻擊可能導致市場波動加劇，並削弱對去中心化交易所公平性和效率的信任。