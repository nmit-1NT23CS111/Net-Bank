export interface LendingApplication {
  id: string
  user: string
  requested_amount: string
  requested_tenure_months: number
  purpose: string
  status: string
  created_at: string
  updated_at: string
}

export interface Lender {
  id: string
  name: string
  minimum_credit_score: number
  maximum_loan_amount: string
  minimum_loan_amount: string
  minimum_interest_rate: string
  maximum_interest_rate: string
  minimum_tenure_months: number
  maximum_tenure_months: number
  active: boolean
  created_at: string
}

export interface CreditAssessment {
  id: string
  user: string
  loan_application: string
  credit_score: number
  risk_category: string
  income_score: number
  expense_score: number
  balance_score: number
  transaction_score: number
  repayment_score: number
  debt_score: number
  maximum_eligible_amount: string
  eligibility: boolean
  decision: string
  reasons: string[]
  risk_factors: string[]
  model_version: string
  input_snapshot: Record<string, unknown>
  created_at: string
  updated_at: string
}

export interface LoanOffer {
  id: string
  loan_application: string
  lender: Lender
  loan_amount: string
  interest_rate: string
  tenure_months: number
  emi: string
  total_interest: string
  total_repayment: string
  offer_score: number
  status: string
  expires_at: string | null
  created_at: string
}

export interface Loan {
  id: string
  loan_application: string
  lender: string
  principal_amount: string
  interest_rate: string
  tenure_months: number
  emi: string
  total_interest: string
  total_repayment: string
  status: string
  disbursed_at: string | null
  created_at: string
}

export interface Repayment {
  id: string
  loan: string
  installment_number: number
  due_date: string
  amount: string
  paid_amount: string
  status: string
  paid_at: string | null
  created_at: string
}

export interface LoanApplicationsResponse {
  success?: boolean
  count?: number
  next?: string | null
  previous?: string | null
  results?: LendingApplication[]
  application?: LendingApplication
  applications?: LendingApplication[]
}

export interface CreditAssessmentResponse {
  success: boolean
  assessment: CreditAssessment
  detail?: string
}

export interface LoanOfferAcceptResponse {
  success: boolean
  loan?: Loan
  detail?: string
}

export interface LoansResponse {
  success?: boolean
  count?: number
  next?: string | null
  previous?: string | null
  results?: Loan[]
  loan?: Loan
}

export interface RepaymentsResponse {
  success?: boolean
  results?: Repayment[]
}
