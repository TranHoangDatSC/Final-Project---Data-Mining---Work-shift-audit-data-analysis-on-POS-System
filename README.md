# POS Transaction Audit Data Mining

## Project Overview
This project focuses on extracting actionable insights from raw POS (Point of Sale) system audit logs. By mining transaction-level data, the system identifies operational discrepancies, potential internal fraud, and optimizes shift-based performance.

## Key Features
- **Data Parsing:** Automates the transformation of semi-structured audit logs into clean, tabular formats.
- **Anomaly Detection:** Flags suspicious activities such as excessive voids, unrecorded no-sales, and high-frequency manual discounts.
- **Shift Analysis:** Compares performance metrics (transaction speed, cash variance) across different shifts and employees.
- **Risk Reporting:** Generates summaries of high-risk transactions that require management review.

## Technical Approach
1. **Extraction:** Cleaning and processing raw text/JSON logs from the POS backend.
2. **Analysis:** Applying pattern matching to identify "sequence-based" fraud (e.g., printing a subtotal followed by a bill cancellation).
3. **Visualization:** Summarizing results into key performance indicators (KPIs) for managers.

## Business Value
Moving beyond simple bookkeeping, this tool turns "dead" log files into a strategic asset to prevent revenue leakage and improve staff accountability.

-- Author: Tran Hoang Dat --