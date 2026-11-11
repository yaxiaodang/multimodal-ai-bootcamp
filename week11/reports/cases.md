# 原始预测摘录（自动选取，每run前两条）

完整错误候选见[JSON](error-candidates.json)，人工复核未完成。

### rank4 / F2000

输入Prompt：
```text
Extract the final total and currency. Return only JSON with string keys total and currency.
Document:
Invoice F2000
Currency: USD
Subtotal: 475.34
Tax: 6.62
Total: 481.96
Answer:

```
参考：`{"total": "481.96", "currency": "USD"}`

训练前：
````text

```

```

```

```

```

```

```

```

```

```

```
````
训练后：
```json
{"total":"481.96","currency":"USD"}
```

### rank4 / F2001

输入Prompt：
```text
Extract the final total and currency. Return only JSON with string keys total and currency.
Document:
Receipt F2001 | Subtotal 670.65 | Tax 6.76 | Total 677.41 EUR
Answer:

```
参考：`{"total": "677.41", "currency": "EUR"}`

训练前：
```text
Total: 677.41 EUR

### Subtotal 677.41 EUR

Subtotal 677.
```
训练后：
```json
{"total":"677.41","currency":"EUR"}
```

### rank8 / F2000

输入Prompt：
```text
Extract the final total and currency. Return only JSON with string keys total and currency.
Document:
Invoice F2000
Currency: USD
Subtotal: 475.34
Tax: 6.62
Total: 481.96
Answer:

```
参考：`{"total": "481.96", "currency": "USD"}`

训练前：
````text

```

```

```

```

```

```

```

```

```

```

```
````
训练后：
```json
{"total":"481.96","currency":"USD"}
```

### rank8 / F2001

输入Prompt：
```text
Extract the final total and currency. Return only JSON with string keys total and currency.
Document:
Receipt F2001 | Subtotal 670.65 | Tax 6.76 | Total 677.41 EUR
Answer:

```
参考：`{"total": "677.41", "currency": "EUR"}`

训练前：
```text
Total: 677.41 EUR

### Subtotal 677.41 EUR

Subtotal 677.
```
训练后：
```json
{"total":"677.41","currency":"EUR"}
```
