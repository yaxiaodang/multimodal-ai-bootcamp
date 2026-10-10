# 完整四组 Prompt

每条文本同时输入对应图像，参考答案不传入模型。固定参数：
```json
{
  "device": "cpu",
  "dtype": "float32",
  "attention": "sdpa",
  "cpu_threads": 4,
  "seed": 42,
  "do_sample": false,
  "max_new_tokens": 128,
  "enable_thinking": false
}
```

## shapes
图像：`samples/shapes.png`

### A
```text
Question: Describe the two colored shapes and their positions in one short sentence.
```

### E
```text
Answer only from visible evidence in the image. If the answer is absent or unreadable, say that you cannot determine it. Question: Describe the two colored shapes and their positions in one short sentence.
```

### S
```text
Keep the answer brief. Question: Describe the two colored shapes and their positions in one short sentence.
```

### B
```text
Answer only from visible evidence in the image. If the answer is absent or unreadable, say that you cannot determine it. Keep the answer brief. Question: Describe the two colored shapes and their positions in one short sentence.
```

## count
图像：`samples/count.png`

### A
```text
Question: How many green circles are visible?
```

### E
```text
Answer only from visible evidence in the image. If the answer is absent or unreadable, say that you cannot determine it. Question: How many green circles are visible?
```

### S
```text
Keep the answer brief. Question: How many green circles are visible?
```

### B
```text
Answer only from visible evidence in the image. If the answer is absent or unreadable, say that you cannot determine it. Keep the answer brief. Question: How many green circles are visible?
```

## position
图像：`samples/position.png`

### A
```text
Question: Is the red rectangle above or below the blue circle?
```

### E
```text
Answer only from visible evidence in the image. If the answer is absent or unreadable, say that you cannot determine it. Question: Is the red rectangle above or below the blue circle?
```

### S
```text
Keep the answer brief. Question: Is the red rectangle above or below the blue circle?
```

### B
```text
Answer only from visible evidence in the image. If the answer is absent or unreadable, say that you cannot determine it. Keep the answer brief. Question: Is the red rectangle above or below the blue circle?
```

## invoice
图像：`samples/invoice.png`

### A
```text
Question: What is the invoice ID? Copy it exactly.
```

### E
```text
Answer only from visible evidence in the image. If the answer is absent or unreadable, say that you cannot determine it. Question: What is the invoice ID? Copy it exactly.
```

### S
```text
Keep the answer brief. Question: What is the invoice ID? Copy it exactly.
```

### B
```text
Answer only from visible evidence in the image. If the answer is absent or unreadable, say that you cannot determine it. Keep the answer brief. Question: What is the invoice ID? Copy it exactly.
```

## dense_text
图像：`samples/dense_text.png`

### A
```text
Question: What code is shown for Record 09? Copy it exactly.
```

### E
```text
Answer only from visible evidence in the image. If the answer is absent or unreadable, say that you cannot determine it. Question: What code is shown for Record 09? Copy it exactly.
```

### S
```text
Keep the answer brief. Question: What code is shown for Record 09? Copy it exactly.
```

### B
```text
Answer only from visible evidence in the image. If the answer is absent or unreadable, say that you cannot determine it. Keep the answer brief. Question: What code is shown for Record 09? Copy it exactly.
```

## table
图像：`samples/table.png`

### A
```text
Question: What is the price of the Book in the table?
```

### E
```text
Answer only from visible evidence in the image. If the answer is absent or unreadable, say that you cannot determine it. Question: What is the price of the Book in the table?
```

### S
```text
Keep the answer brief. Question: What is the price of the Book in the table?
```

### B
```text
Answer only from visible evidence in the image. If the answer is absent or unreadable, say that you cannot determine it. Keep the answer brief. Question: What is the price of the Book in the table?
```

## chart
图像：`samples/chart.png`

### A
```text
Question: Which labeled bar is tallest?
```

### E
```text
Answer only from visible evidence in the image. If the answer is absent or unreadable, say that you cannot determine it. Question: Which labeled bar is tallest?
```

### S
```text
Keep the answer brief. Question: Which labeled bar is tallest?
```

### B
```text
Answer only from visible evidence in the image. If the answer is absent or unreadable, say that you cannot determine it. Keep the answer brief. Question: Which labeled bar is tallest?
```

## arithmetic
图像：`samples/arithmetic.png`

### A
```text
Question: What is the total cost in USD?
```

### E
```text
Answer only from visible evidence in the image. If the answer is absent or unreadable, say that you cannot determine it. Question: What is the total cost in USD?
```

### S
```text
Keep the answer brief. Question: What is the total cost in USD?
```

### B
```text
Answer only from visible evidence in the image. If the answer is absent or unreadable, say that you cannot determine it. Keep the answer brief. Question: What is the total cost in USD?
```

## missing_date
图像：`samples/missing_date.png`

### A
```text
Question: What purchase date is shown on the receipt?
```

### E
```text
Answer only from visible evidence in the image. If the answer is absent or unreadable, say that you cannot determine it. Question: What purchase date is shown on the receipt?
```

### S
```text
Keep the answer brief. Question: What purchase date is shown on the receipt?
```

### B
```text
Answer only from visible evidence in the image. If the answer is absent or unreadable, say that you cannot determine it. Keep the answer brief. Question: What purchase date is shown on the receipt?
```

## occluded
图像：`samples/occluded.png`

### A
```text
Question: What is the full account code?
```

### E
```text
Answer only from visible evidence in the image. If the answer is absent or unreadable, say that you cannot determine it. Question: What is the full account code?
```

### S
```text
Keep the answer brief. Question: What is the full account code?
```

### B
```text
Answer only from visible evidence in the image. If the answer is absent or unreadable, say that you cannot determine it. Keep the answer brief. Question: What is the full account code?
```
