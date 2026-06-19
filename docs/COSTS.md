# Cost Analysis Methodology (Planned)

> **STATUS: STAGE 0 — METHODOLOGY ONLY.** This document defines *how* the On-Prem-vs-API
> cost analysis will be performed. **It contains no numbers, no prices, and no results.**
> All figures are produced in Stage 6 from real measurements and dated, cited pricing, with
> every assumption parameterized in `config/` (not hardcoded).

---

## 1. Objective

Determine when running the model **On-Premises** is more cost-effective than calling an
**external API**, and express it as a **break-even point** (in requests and/or tokens).
Optionally add a third line: **cloud GPU rental** (assignment §5.5, optional).

## 2. Cost components

### 2.1 External API cost (per request)
```
api_cost_per_request = (input_tokens / 1e6)  * price_input_per_M_tokens
                     + (output_tokens / 1e6) * price_output_per_M_tokens
```
- `input_tokens`, `output_tokens`: measured from the actual task (Stage 5).
- Prices: from the chosen provider's published rate, **dated and cited** at analysis time
  (provider/ADR-0104). Prompt/context caching effects considered and noted if relevant.

### 2.2 On-Prem cost (per request)
```
onprem_cost_per_request = amortized_capex_per_request + opex_per_request
```
- **CAPEX (amortized):**
  ```
  amortized_capex_per_request = hardware_cost / (useful_life_requests)
  useful_life_requests        = (lifetime_years * uptime_hours_per_year * requests_per_hour)
  requests_per_hour           = 3600 / measured_runtime_seconds_per_request
  ```
- **OPEX (per request):**
  ```
  energy_kWh_per_request = (avg_power_watts * measured_runtime_seconds_per_request) / 3.6e6
  electricity_cost       = energy_kWh_per_request * electricity_price_per_kWh
  opex_per_request       = electricity_cost + maintenance_allocation_per_request
  ```

### 2.3 Cloud GPU rental (optional third line)
```
cloud_cost_per_request = hourly_gpu_rate * (measured_runtime_seconds_per_request / 3600)
```

## 3. Energy estimation method

Energy is an **estimate**, explicitly labelled as such:
```
energy_kWh = (avg_power_watts * total_runtime_seconds) / 3.6e6
```
- `avg_power_watts`: from a documented source per component path —
  - GPU: `nvidia-smi` power draw sampling if a GPU is used; else
  - CPU/system: device TDP or a measured/typical figure, with the source stated.
- All power assumptions recorded with their origin; no invented wattages.

## 4. Break-even computation

Find `N` (requests) where cumulative costs cross:
```
onprem_total(N) = hardware_cost + N * opex_per_request
api_total(N)    = N * api_cost_per_request
break_even_N    = hardware_cost / (api_cost_per_request - opex_per_request)
                  # valid only when api_cost_per_request > opex_per_request
```
- If `api_cost_per_request <= opex_per_request`, On-Prem never breaks even on OPEX alone —
  that itself is a reportable finding.
- Plotted as cumulative cost vs request count, with the crossover annotated
  (`figures/breakeven.*`), optionally including the cloud-GPU line.

## 5. Inputs required (sourced later, never invented)

| input | source | stage |
| --- | --- | --- |
| `input_tokens`, `output_tokens` per request | measured task | 5 |
| `measured_runtime_seconds_per_request` | metrics | 5 |
| `avg_power_watts` | `nvidia-smi` / documented TDP | 5–6 |
| `electricity_price_per_kWh` | local tariff (user/region) — `NEEDED_USER_INPUT` if unknown | 6 |
| `hardware_cost` | actual/representative price, cited | 6 |
| `lifetime_years`, `uptime_hours_per_year` | stated assumptions | 6 |
| `price_input/output_per_M_tokens` | provider, dated & cited (ADR-0104) | 6 |
| `hourly_gpu_rate` (optional) | cloud provider, dated & cited | 6 |

## 6. Reporting rules

- Every assumption (prices, power, lifetime, utilization) is **explicit and parameterized**
  in `config/` so the analysis is transparent and reproducible (assignment §5.5).
- Estimates are labelled "estimate"; measurements are labelled "measured".
- Sensitivity: where a result hinges on a soft assumption (e.g., electricity price), show
  how the break-even shifts across a plausible range.
- No price, energy figure, or break-even number appears anywhere until backed by Stage 5–6
  evidence.

## 7. Current status

No costs computed. This is methodology only. The candidate **break-even simulator** is also
a candidate for the original extension (R-EXT-01 / ADR-0105).
