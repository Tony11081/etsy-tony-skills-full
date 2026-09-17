# Supplier Evaluation, Cost Model, and Equipment Investment

Use in FULL-B for production-route decisions and in FULL-C for price/margin readiness. This reference supports decisions; it does not authorize purchases, contracts, supplier orders, or equipment investment.

## Supplier evaluation

Evaluate the exact supplier/process/material scope, not the company name in general.

| Dimension | Required evidence |
|---|---|
| Identity and scope | legal/business identity where relevant, location, contact, exact product/process/material service |
| Technical fit | material/finish capability, geometry/size, process detail, personalization, files, fixture/tooling, finishing |
| Sample quality | dated sample IDs, approved criteria, defects, photos/measurements, repeatability |
| Quality system | incoming/process/final checks, traceability, nonconformance, rework, change notification |
| Capacity and lead time | documented normal/peak capacity, setup, production, transit, rush limits; date-stamped |
| Commercial terms | quote date/currency, MOQ, tooling/setup, unit tiers, sample, packaging, freight/duty, payment terms |
| Ownership and continuity | artwork/tooling/mold/die ownership, portability, backup route, material substitution policy |
| Compliance and claims | material, safety/contact/care/environmental documents relevant to the Product |
| Personalization/data handling | order-data transfer, access, retention, proof, deletion, confidentiality, error handling |
| Communication and service | response, escalation, language/time zone, corrective action, account ownership |

Supplier status: Research / Quote Pending / Sample Required / Conditional / Approved for Exact Scope / Hold / Rejected. Approval applies only to the tested scope and current evidence.

Use at least one comparison route when practical: internal, primary supplier, alternate supplier, or substitute process. Do not fabricate supplier availability or quote values.

## Cost model

Use USD for US-market decisions and record quote/exchange dates. Keep Unknown fields visible.

### Unit cost components

- landed blank/material/component cost;
- direct process or outsource unit cost;
- direct labor by actual time study and loaded rate;
- setup/tooling allocation by stated batch assumption;
- consumables and finishing;
- personalization proof/manual review;
- inspection, rework, expected waste/defect based on evidence;
- packaging and inserts;
- inbound/outbound freight, duty/tax where applicable;
- platform/payment/advertising/other variable fees verified at calculation time;
- overhead allocation under the business's approved method.

Do not hide setup, proof, packaging, failure, or outsourced finishing inside an unexplained estimate.

### Core calculations

`Total Variable Unit Cost = sum of all variable unit components`

`Contribution per Unit = Net Selling Price − Total Variable Unit Cost`

`Contribution Margin % = Contribution per Unit ÷ Net Selling Price × 100`

`Break-even Units = Fixed Development and Setup Cost ÷ Contribution per Unit`

If contribution is zero/negative or an input is Unknown, mark the result Not Decision-Ready rather than forcing a value.

Run at least low/base/high volume scenarios using documented assumptions. Separate price, discounts, tax, shipping charged to customer, refunds/returns, and ad spend so decision-makers can see what changes.

## Commercial readiness gate

Before a Listing Launch Pack is release-ready, record:

- verified Product/production cost inputs or explicit approved provisional status;
- target selling price and evidence date;
- contribution/margin direction;
- setup/tooling recovery assumption;
- manual proof/option complexity cost;
- sample/QC/packaging cost;
- supplier lead-time and reorder risk;
- price/claim consistency with the actual Product.

A Commercial Potential score is not a cost model and cannot replace these inputs.

## Equipment investment evaluation

First preserve the Ideal Process, internal alternative, and outsource route. Evaluate equipment only after a recurring verified demand/quality/cost problem exists.

Record:

- exact capability gap and required quality/process scope;
- current outsource/internal baseline with volume, cost, lead, defects, labor, and constraints;
- candidate equipment model/configuration and authoritative documentation;
- facility, electrical/ventilation/safety/regulatory, software, tooling, fixture, consumable, maintenance, calibration, training, insurance, and staffing needs;
- usable work area/material/process/detail evidence and required acceptance test;
- acquisition, freight/duty, installation, financing, depreciation/accounting, service, downtime, scrap/ramp, and working-capital cost;
- low/base/high utilization and demand scenarios;
- supplier/outsourcing backup after investment;
- responsible owner and approval authority.

### Investment calculations

`Annual Net Benefit = Avoided Outsource/Operating Cost + Incremental Contribution − New Annual Operating Cost`

`Simple Payback = Total Initial Investment ÷ Annual Net Benefit`

`Simple ROI % = Annual Net Benefit ÷ Total Initial Investment × 100`

These are screens, not a purchase decision. If demand, quality, safety, facility, capability, or cost inputs are Unknown, classify `Equipment Investment Candidate — Validation Required`.
