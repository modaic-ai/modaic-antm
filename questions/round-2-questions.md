# Validation Evaluations - Round 3

Questions 31-50 (20 questions)

---

## the products that get bought together

**Question:** Find the product pair with highest co-purchase rate, what are the items (pair in ascending order) and how many times have they been bought together. Our competitor prices almost everything 5% cheaper than us, what could we make the bundle price to come just under the competitors combined price for these items (let's undercut them by 1%)?

**Observations:**

```json
{
  "question": "string",
  "item_1_sk": "int",
  "item_2_sk": "int",
  "competitor_combined_price": "float",
  "bundle_price": "float",
  "difficulty": "int"
}
```

---

## the traffic that comes from bots

**Question:** November 2022 shows record pageviews but flat revenue. We think it's bots. What percentage of web traffic in November is likely due to bots?

**Observations:**

```json
{
  "question": "string",
  "total_pageviews": "int",
  "bot_ip_prefix": "string",
  "bot_pageviews": "int",
  "bot_percentage": "float",
  "difficulty": "int"
}
```

---

## the warehouse that needs validation

**Question:** Our CS team is getting a lot of tickets related to out-of-stock in January 2022. Can you determine if any specific warehouse is taking a long time to receive restocks? What percentage of the out-of-stock CS tickets are related to that warehouse?

**Observations:**

```json
{
  "question": "string",
  "slowest_warehouse_sk": "int",
  "avg_days_to_receive_shipment": "float",
  "cs_ticket_percentage": "float",
  "difficulty": "int"
}
```

---

## the promise that needs validation

**Question:** What percent of orders missed our delivery time-frame promise, and which product category performed worst?

**Observations:**

```json
{
  "question": "string",
  "promise_days": "int",
  "on_time_rate_percent": "float",
  "missed_rate_percent": "float",
  "worst_category": "string",
  "worst_category_on_time_rate_percent": "float",
  "difficulty": "int"
}
```

---

## the vendor that owes rebates

**Question:** Finance says our supplier owes us a Q4 2022 rebate for missing their speedy delivery guarantee. How much rebate are we owed?

**Observations:**

```json
{
  "question": "string",
  "q4_2022_on_time_rate_percent": "float",
  "sla_threshold_percent": "float",
  "rebate_owed": "float",
  "difficulty": "int"
}
```

---

## the requests that go overdue

**Question:** Since July 1, 2018, what percentage of customer data deletion requests were completed within the legal requirement of 30 days, and how many are overdue?

**Observations:**

```json
{
  "question": "string",
  "total_requests": "int",
  "overdue_requests": "int",
  "overdue_rate_percent": "float",
  "difficulty": "int"
}
```

---

## the products that need recall

**Question:** Our quality team noticed a spike in product defect reports in late 2020. We're investigating whether this warrants a product recall. What percentage of defect reports in Q4 2020 were classified as 'critical' or 'high' severity, and which product category had the highest concentration of these severe defects?

**Observations:**

```json
{
  "question": "string",
  "q4_2020_defect_reports": "int",
  "critical_high_severity_percent": "float",
  "worst_category": "string",
  "worst_category_severe_percentage": "float",
  "difficulty": "int"
}
```

---

## the cohorts that have age gaps

**Question:** We have a customer gap in the 25-30 age range (assume today is 2023-12-31). Based on the linear relationship between age and average customer value across other age groups, calculate the ACV for this cohort and the revenue opportunity from doubling its size. Submit ACV and revenue opportunity.

**Observations:**

```json
{
  "question": "string",
  "age_25_30_customer_count": "int",
  "average_other_buckets": "float",
  "acv_25_30": "float",
  "revenue_opportunity": "float",
  "difficulty": "int"
}
```

---

## the customer who migrates channels

**Question:** Customer SK 33,333 switched from 100% in-store to 100% online in March 2021. Investigate what event triggered this channel migration, paying particular attention to any returns and their associated return reasons during this period.

**Observations:**

```json
{
  "question": "string",
  "returns_in_march_2021": "int",
  "return_store_sk": "int",
  "return_reason": "string",
  "difficulty": "int"
}
```

---

## the state that generates profit from NY

**Question:** How much net profit did we make from NY state in 2023?

**Observations:**

```json
{
  "question": "string",
  "net_profit": "float",
  "difficulty": "int"
}
```

---

## the months that needs validation

**Question:** What two months have the highest revenue generally?

**Observations:**

```json
{
  "question": "string",
  "highest_revenue_months": "list[string]",
  "difficulty": "int"
}
```

---

## the month that hits maximum sales

**Question:** What month/year did we hit maximum sales?

**Observations:**

```json
{
  "question": "string",
  "month": "int",
  "year": "int",
  "difficulty": "int"
}
```

---

## the state that has highest profit

**Question:** Which state currently has the highest cumulative net profit dollar amount?

**Observations:**

```json
{
  "question": "string",
  "state": "string",
  "cumulative_profit": "float",
  "difficulty": "int"
}
```

---

## the state that has highest profit per customer

**Question:** Which state has the highest net profit per customer?

**Observations:**

```json
{
  "question": "string",
  "state": "string",
  "profit_per_customer": "float",
  "difficulty": "int"
}
```

---

## the supplier that packs efficiently

**Question:** Our warehouse wants to optimize receiving operations by identifying suppliers that pack most efficiently. Which supplier has the highest average monetary value per pallet received? What is their average value per pallet?

**Observations:**

```json
{
  "question": "string",
  "top_supplier": "string",
  "avg_value_per_pallet": "float",
  "difficulty": "int"
}
```

---

## the item that exceeds baseline sales

**Question:** Item SK 54,321 sells at different discount levels. At which discount level does quantity sold first exceed 10x the baseline, and what's the total revenue at that level?

**Observations:**

```json
{
  "question": "string",
  "discount_pct": "int",
  "quantity": "int",
  "revenue": "float",
  "difficulty": "int"
}
```

---

## the store that gets cannibalized

**Question:** Store #7 experienced cannibalization from a new store opening in H2 2021. For the category that saw the largest revenue impact calculate the net delta with the new store. Submit the category name and net dollar amount.

**Observations:**

```json
{
  "question": "string",
  "cannibalizing_store_sk": "int",
  "cannibalized_store_sk": "int",
  "category": "string",
  "net_delta": "float",
  "difficulty": "int"
}
```

---

## the customers who represent their segments

**Question:** Segment customers by income tier (Low: <$50K, Medium: $50-100K, High: $100K+) and age group (Young: born <1970, Old: ≥1970). For the top 3 segments by total revenue, identify the 3 most exemplar customers in each segment (closest to segment median CLV). What is the most commonly purchased item across those 9 exemplar customers? Submit item SK and purchase count.

**Observations:**

```json
{
  "question": "string",
  "item_sk": "int",
  "purchase_count": "int",
  "difficulty": "int"
}
```

---

## the cohorts that retain poorly

**Question:** It seems like Q4 customer cohorts retain worse at 90 days. If those customers retained at the same average rate as those acquired in other quarters, what would the additional revenue have been? Submit total cohort LTV and lost 90-day revenue.

**Observations:**

```json
{
  "question": "string",
  "q4_cohort_size": "int",
  "q4_retention_rate": "float",
  "lost_90_day_revenue": "float",
  "difficulty": "int"
}
```

---

## the promotion that tests free shipping

**Question:** A free shipping promotion in July 2022 (orders >$50) ran for one month on a test group. Calculate average order value for test vs control, and incremental revenue per customer. Submit the promotion number, how many users benefit from it, and the incremental revenue per customer.

**Observations:**

```json
{
  "question": "string",
  "promotion_sk": "int",
  "test_aov": "float",
  "control_aov": "float",
  "incremental_aov": "float",
  "incremental_revenue_per_customer": "float",
  "difficulty": "int"
}
```

---
