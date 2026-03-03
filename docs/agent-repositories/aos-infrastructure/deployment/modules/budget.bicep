// budget.bicep — Azure Cost Management budget for AOS governance
// Creates a monthly budget with percentage-threshold alert notifications.

@description('Deployment environment (dev, staging, prod)')
param environment string

@description('Monthly budget limit in the subscription currency')
param budgetAmount int = 500

@description('Budget alert threshold percentages (0–100)')
param alertThresholds array = [50, 80, 100]

@description('Email addresses to notify when a threshold is crossed')
param contactEmails array = []

@description('Start date for the budget (YYYY-MM-DD). Defaults to first day of current month.')
param startDate string = ''

@description('End date for the budget (YYYY-MM-DD). Defaults to last day of current year.')
param endDate string = ''

// ── Resolve default dates ────────────────────────────────────────────────────
var resolvedStartDate = empty(startDate) ? '${string(utcNow('yyyy'))}-${string(utcNow('MM'))}-01' : startDate
var resolvedEndDate   = empty(endDate)   ? '${string(utcNow('yyyy'))}-12-31' : endDate

// ── Budget name ──────────────────────────────────────────────────────────────
var budgetName = 'aos-budget-${environment}'

// ── Threshold notifications ──────────────────────────────────────────────────
// Build notification object from the alertThresholds and contactEmails arrays.
// Each threshold gets a unique notification key.
var notifications = reduce(alertThresholds, {}, (acc, threshold) => union(acc, {
  'threshold-${threshold}': {
    enabled: true
    operator: 'GreaterThanOrEqualTo'
    threshold: threshold
    contactEmails: contactEmails
    contactRoles: ['Owner', 'Contributor']
    thresholdType: 'Actual'
  }
}))

// ── Budget resource ──────────────────────────────────────────────────────────
resource budget 'Microsoft.Consumption/budgets@2021-10-01' = {
  name: budgetName
  properties: {
    category: 'Cost'
    amount: budgetAmount
    timeGrain: 'Monthly'
    timePeriod: {
      startDate: resolvedStartDate
      endDate: resolvedEndDate
    }
    notifications: notifications
  }
}

// ── Outputs ──────────────────────────────────────────────────────────────────
output budgetId string = budget.id
output budgetName string = budget.name
output budgetAmount int = budgetAmount
