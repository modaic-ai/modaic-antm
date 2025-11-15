# Validation Evaluations - Round 2

Questions 11-30 (20 questions)

---

## the quarter that succeeds most

**Question:** What was our most successful quarter by far (by total net profit)?

**Observations:**

```json
{
  "question": "string",
  "successful_quarter": "string",
  "difficulty": "int"
}
```
---

## the channel that generates least revenue

**Question:** What is the smallest channel in terms of percent of Revenue?

**Observations:**

```json
{
  "question": "string",
  "smallest_channel": "string",
  "store_revenue_percent": "float",
  "web_revenue_percent": "float",
  "catalog_revenue_percent": "float",
  "difficulty": "int"
}
```

---

## the item that sells most

**Question:** What is the top selling item of 2023? Give me the product name

**Observations:**

```json
{
  "question": "string",
  "item_sk": "int",
  "difficulty": "int"
}
```

---

## the transaction that needs validation

**Question:** What is the highest single transaction for a store ever in terms of net profit?

**Observations:**

```json
{
  "question": "string",
  "highest_net_profit": "float",
  "ticket_number": "int",
  "store_sk": "int",
  "difficulty": "int"
}
```

---

## the revenue that needs validation

**Question:** For that same transaction with the highest net profit, what was the total revenue (not including taxes)?

**Observations:**

```json
{
  "question": "string",
  "total_revenue": "float",
  "net_profit": "float",
  "difficulty": "int"
}
```

---

## the stores that exist

**Question:** How many unique stores are there?

**Observations:**

```json
{
  "question": "string",
  "unique_stores": "int",
  "difficulty": "int"
}
```

---

## the store that has highest lifetime profit

**Question:** What stores has highest total net profit over its lifetime?

**Observations:**

```json
{
  "question": "string",
  "store_sk": "int",
  "difficulty": "int"
}
```

---

## the store that has lowest lifetime profit

**Question:** What store has the lowest net profit over its lifetime?

**Observations:**

```json
{
  "question": "string",
  "store_sk": "int",
  "difficulty": "int"
}
```

---

## the state that has most customers

**Question:** From which state do we have the most customers?

**Observations:**

```json
{
  "question": "string",
  "state": "string",
  "customer_count": "int",
  "difficulty": "int"
}
```

---

## the approver that misses signatures

**Question:** Our compliance audit found high-value purchase orders missing required approver signatures, creating financial liability. Purchase orders over $10,000 require both buyer and approver signatures per our procurement policy. What is the total value of unsigned purchase orders exceeding the $10,000 threshold, which approver has the highest total dollar value of unsigned orders, and what is that value?

**Observations:**

```json
{
  "question": "string",
  "total_unsigned_value": "float",
  "highest_value_approver": "string",
  "highest_value_approver_total": "float",
  "difficulty": "int"
}
```

---

## the door dock that damages most

**Question:** Our warehouse operations team at Warehouse 2 has noticed an increase in damaged inventory during 2020. We suspect certain door docks may be causing more damage than others. Identify which door dock has the highest damage rate and quantify how much worse it is compared to the facility average.

**Observations:**

```json
{
  "question": "string",
  "highest_damage_dock": "string",
  "highest_damage_rate_pct": "float",
  "avg_damage_rate_pct": "float",
  "rate_multiplier": "float",
  "difficulty": "int"
}
```

---

## the subscriber who needs recurring orders

**Question:** Our largest customer in 2022 should sign up for a recurring order program. Which customer, which item, and how many months did they order that item?

**Observations:**

```json
{
  "question": "string",
  "customer_sk": "int",
  "item_sk": "int",
  "num_months": "int",
  "difficulty": "int"
}
```

---

## the promotion that drives signups

**Question:** We ran a signup promotion #102 in Q1 2020 for $20 off their first order. Calculate its ROI based on 12-mo value assuming all signups are incremental.

**Observations:**

```json
{
  "question": "string",
  "cohort_size": "int",
  "cohort_ltv": "float",
  "roi_pct": "float",
  "net_profit": "float",
  "difficulty": "int"
}
```

---

## the transactions that look fraudulent

**Question:** We have fishy transactions in December 2022. Based on our fraud policy, how much total sales seem suspiciously close to our fraud spending limit?

**Observations:**

```json
{
  "question": "string",
  "customer_sk": "int",
  "transaction_count": "int",
  "total_value": "float",
  "difficulty": "int"
}
```

---

## the items that get returned most

**Question:** Identify the bottom decile of items (worst 10% by return rate). Calculate the net revenue impact from carrying these high-return items, accounting for sales revenue, customer refunds, and restocking costs. What is the total net revenue impact?

**Observations:**

```json
{
  "question": "string",
  "bottom_decile_item_count": "int",
  "total_restocking_costs": "float",
  "net_revenue_impact": "float",
  "difficulty": "int"
}
```

---

## the item that sells seasonally

**Question:** Identify the item with the strongest seasonal sales pattern, where 3 consecutive calendar months account for the highest percentage of its annual sales. Report the item SK and the percentage of annual sales that these 3 peak months represent (rounded to nearest whole percent).

**Observations:**

```json
{
  "question": "string",
  "item_sk": "int",
  "peak_months": "list[int]",
  "percentage": "int",
  "difficulty": "int"
}
```

---

## the item that exceeds baseline at discount

**Question:** One item was sold at exactly 4 different discount levels in 2022 (0%, 10%, 15%, 20%). Find this item and calculate: (1) the discount percentage where quantity sold first exceeds 2x the baseline, and (2) the discount level that maximizes revenue. Submit item SK, both discount percentages, and max revenue.

**Observations:**

```json
{
  "question": "string",
  "item_sk": "int",
  "doubling_discount": "int",
  "max_revenue_discount": "int",
  "max_revenue": "float",
  "difficulty": "int"
}
```

---

## the performance that needs validation

**Question:** Store #15 has highest revenue but lowest profit margin. Is our promotion strategy causing an issue? Quantify the impact.

**Observations:**

```json
{
  "question": "string",
  "store_sk": "int",
  "profit_margin_percent": "float",
  "promotional_sales_percent": "float",
  "lost_profit": "float",
  "difficulty": "int"
}
```

---

## the customers who stay loyal to brands

**Question:** Long-tenure customers (active 24+ months) show monthly repeat purchase behavior concentrated in one brand. Calculate which brand and what percentage of long-tenure customers purchase from this brand each month on average.

**Observations:**

```json
{
  "question": "string",
  "long_tenure_customer_count": "int",
  "loyalty_brand": "null",
  "monthly_repurchase_rate_percent": "float",
  "difficulty": "int"
}
```

---

## the deviation that needs validation

**Question:** November 2022 month-over-month growth was below trend. Which store had the largest negative deviation from its 3-month linear trend? What percentage of the total shortfall in trend was this responsible for?

**Observations:**

```json
{
  "question": "string",
  "worst_store_sk": "int",
  "deviation_percentage_points": "float",
  "contribution_percent": "float",
  "difficulty": "int"
}
```

---
