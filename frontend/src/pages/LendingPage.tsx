import React, { FormEvent, useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { apiService } from '@/services/api.service'
import { getApiErrorMessage } from '@/utils/apiErrors'
import { formatCurrency, formatDate } from '@/utils/helpers'
import { CreditAssessment, LendingApplication, Loan, LoanOffer, Repayment } from '@/models/lending.models'

const initialApplication = {
  requested_amount: '',
  requested_tenure_months: '24',
  purpose: 'PERSONAL',
}

export const LendingPage: React.FC = () => {
  const navigate = useNavigate()
  const [applications, setApplications] = useState<LendingApplication[]>([])
  const [offers, setOffers] = useState<LoanOffer[]>([])
  const [loans, setLoans] = useState<Loan[]>([])
  const [repayments, setRepayments] = useState<Record<string, Repayment[]>>({})
  const [selectedApplicationId, setSelectedApplicationId] = useState('')
  const [assessment, setAssessment] = useState<CreditAssessment | null>(null)
  const [form, setForm] = useState(initialApplication)
  const [status, setStatus] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const loadAll = async () => {
    setError('')
    const [appRes, , loanRes] = await Promise.all([
      apiService.getLoanApplications(),
      apiService.getLenders(),
      apiService.getLoans(),
    ])

    const appList = appRes.applications ?? appRes.results ?? []
    setApplications(appList)
    setSelectedApplicationId((current) => current || appList[0]?.id || '')
    setLoans(loanRes.results ?? [])

    for (const loan of loanRes.results ?? []) {
      const repaymentRes = await apiService.getRepayments(loan.id)
      setRepayments((prev) => ({ ...prev, [loan.id]: repaymentRes.results ?? [] }))
    }
  }

  useEffect(() => {
    loadAll()
      .catch((err) => {
        setError(getApiErrorMessage(err, 'Unable to load lending data.'))
      })
      .finally(() => {
        setIsLoading(false)
      })
  }, [])

  useEffect(() => {
    if (!selectedApplicationId) return
    apiService
      .getCreditAssessment(selectedApplicationId)
      .then((result) => {
        setAssessment(result.assessment)
      })
      .catch(() => setAssessment(null))
  }, [selectedApplicationId])

  const activeApplication = useMemo(
    () => applications.find((app) => app.id === selectedApplicationId) ?? applications[0],
    [applications, selectedApplicationId]
  )

  const handleCreateApplication = async (event: FormEvent) => {
    event.preventDefault()
    setIsSubmitting(true)
    setError('')
    setStatus('')

    try {
      const payload = {
        requested_amount: form.requested_amount,
        requested_tenure_months: Number(form.requested_tenure_months),
        purpose: form.purpose,
      }
      const result = await apiService.createLoanApplication(payload)
      const app = result.application ?? result
      setApplications((prev) => [app, ...prev])
      setSelectedApplicationId(app.id)
      setForm(initialApplication)
      setStatus('Loan application created successfully.')
    } catch (err) {
      setError(getApiErrorMessage(err, 'Unable to create loan application.'))
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleSubmitApplication = async (applicationId: string) => {
    setIsSubmitting(true)
    setError('')
    setStatus('')

    try {
      const result = await apiService.submitLoanApplication(applicationId)
      const updated = result.application ?? result
      setApplications((prev) => prev.map((item) => (item.id === applicationId ? { ...item, ...updated } : item)))
      setStatus('Application submitted for evaluation.')
    } catch (err) {
      setError(getApiErrorMessage(err, 'Unable to submit application.'))
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleEvaluate = async (applicationId: string) => {
    setIsSubmitting(true)
    setError('')
    setStatus('')

    try {
      const result = await apiService.evaluateLoanApplication(applicationId)
      setOffers(result.offers ?? [])
      if (result.assessment) setAssessment(result.assessment)
      if (result.application) {
        setApplications((prev) => prev.map((item) => (item.id === applicationId ? { ...item, ...result.application } : item)))
      }
      setStatus(result.decision ? `Decision: ${result.decision}` : 'Application evaluated.')
    } catch (err) {
      setError(getApiErrorMessage(err, 'Unable to evaluate application.'))
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleAcceptOffer = async (offerId: string) => {
    setIsSubmitting(true)
    setError('')
    setStatus('')

    try {
      const result = await apiService.acceptLoanOffer(offerId)
      if (result.success) {
        setStatus('Offer accepted and loan created successfully.')
        const refreshed = await apiService.getLoans()
        setLoans(refreshed.results ?? [])
      }
    } catch (err) {
      setError(getApiErrorMessage(err, 'Unable to accept offer.'))
    } finally {
      setIsSubmitting(false)
    }
  }

  const handlePayRepayment = async (repaymentId: string, paymentAmount: string) => {
    setIsSubmitting(true)
    setError('')
    setStatus('')

    try {
      const result = await apiService.payRepayment(repaymentId, { payment_amount: paymentAmount })
      setStatus(result.message || 'Payment recorded successfully.')
      for (const loan of loans) {
        const repaymentRes = await apiService.getRepayments(loan.id)
        setRepayments((prev) => ({ ...prev, [loan.id]: repaymentRes.results ?? [] }))
      }
    } catch (err) {
      setError(getApiErrorMessage(err, 'Unable to process payment.'))
    } finally {
      setIsSubmitting(false)
    }
  }

  if (isLoading) {
    return <div className="loading-container">Loading lending workspace...</div>
  }

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <div className="header-content">
          <div>
            <p className="eyebrow">Net Bank</p>
            <h1>AI Lending Workspace</h1>
          </div>
          <div className="user-info">
            <button type="button" className="logout-btn" onClick={() => navigate('/dashboard')}>
              Back to dashboard
            </button>
          </div>
        </div>
      </header>

      <main className="dashboard-main">
        {error && <p className="alert alert-error">{error}</p>}
        {status && <p className="alert alert-success">{status}</p>}

        <section className="workspace-grid">
          <form className="tool-panel" onSubmit={handleCreateApplication}>
            <div className="section-heading">
              <h2>New Loan Application</h2>
            </div>

            <label>
              <span>Amount</span>
              <input
                type="number"
                min="1000"
                step="0.01"
                value={form.requested_amount}
                onChange={(event) => setForm((prev) => ({ ...prev, requested_amount: event.target.value }))}
                required
              />
            </label>

            <label>
              <span>Tenure (months)</span>
              <input
                type="number"
                min="1"
                max="360"
                value={form.requested_tenure_months}
                onChange={(event) => setForm((prev) => ({ ...prev, requested_tenure_months: event.target.value }))}
                required
              />
            </label>

            <label>
              <span>Purpose</span>
              <select
                value={form.purpose}
                onChange={(event) => setForm((prev) => ({ ...prev, purpose: event.target.value }))}
              >
                <option value="PERSONAL">Personal</option>
                <option value="HOME">Home</option>
                <option value="AUTO">Auto</option>
                <option value="EDUCATION">Education</option>
                <option value="BUSINESS">Business</option>
              </select>
            </label>

            <button type="submit" className="primary-btn" disabled={isSubmitting}>
              Create application
            </button>
          </form>

          <div className="tool-panel">
            <div className="section-heading">
              <h2>Application Pipeline</h2>
            </div>
            <label>
              <span>Select application</span>
              <select
                value={selectedApplicationId}
                onChange={(event) => setSelectedApplicationId(event.target.value)}
              >
                <option value="" disabled>
                  Choose application
                </option>
                {applications.map((application) => (
                  <option key={application.id} value={application.id}>
                    {application.purpose} • {formatCurrency(application.requested_amount, 'INR')}
                  </option>
                ))}
              </select>
            </label>

            {activeApplication && (
              <div className="stacked-box">
                <p><strong>Status:</strong> {activeApplication.status}</p>
                <p><strong>Amount:</strong> {formatCurrency(activeApplication.requested_amount, 'INR')}</p>
                <p><strong>Tenure:</strong> {activeApplication.requested_tenure_months} months</p>
                <div className="button-row">
                  <button type="button" className="primary-btn" onClick={() => handleSubmitApplication(activeApplication.id)} disabled={isSubmitting}>
                    Submit
                  </button>
                  <button type="button" className="primary-btn" onClick={() => handleEvaluate(activeApplication.id)} disabled={isSubmitting}>
                    Evaluate
                  </button>
                </div>
              </div>
            )}
          </div>
        </section>

        <section className="content-section">
          <div className="section-heading">
            <h2>Credit Assessment</h2>
          </div>

          {assessment ? (
            <>
              <div className="assessment-grid">
                <div className="mini-card">
                  <span>Credit score</span>
                  <strong>{assessment.credit_score}</strong>
                </div>
                <div className="mini-card">
                  <span>Risk</span>
                  <strong>{assessment.risk_category}</strong>
                </div>
                <div className="mini-card">
                  <span>Decision</span>
                  <strong>{assessment.decision}</strong>
                </div>
                <div className="mini-card">
                  <span>Max eligible</span>
                  <strong>{formatCurrency(assessment.maximum_eligible_amount, 'INR')}</strong>
                </div>
                <div className="mini-card">
                  <span>Eligibility</span>
                  <strong>{assessment.eligibility ? 'Eligible' : 'Not eligible'}</strong>
                </div>
              </div>
              <div className="stacked-box">
                <p><strong>Decision reasons</strong></p>
                <ul>
                  {assessment.reasons.map((reason) => <li key={reason}>{reason}</li>)}
                </ul>
                <p><strong>Risk factors</strong></p>
                <ul>
                  {assessment.risk_factors.map((factor) => <li key={factor}>{factor}</li>)}
                </ul>
              </div>
            </>
          ) : (
            <p className="empty-state">No credit assessment yet for the selected application.</p>
          )}
        </section>

        <section className="content-section">
          <div className="section-heading">
            <h2>Matched Lenders & Offers</h2>
          </div>

          {offers.length > 0 ? (
            <div className="offers-list">
              {offers.map((offer) => (
                <div key={offer.id} className="offer-card">
                  <div>
                    <h3>{offer.lender.name}</h3>
                    <p>{offer.lender.minimum_interest_rate}% to {offer.lender.maximum_interest_rate}% APR</p>
                  </div>
                  <div className="offer-metrics">
                    <span>Amount: {formatCurrency(offer.loan_amount, 'INR')}</span>
                    <span>EMI: {formatCurrency(offer.emi, 'INR')}</span>
                    <span>Tenure: {offer.tenure_months} months</span>
                    <span>Offer score: {offer.offer_score}</span>
                  </div>
                  <button type="button" className="primary-btn" onClick={() => handleAcceptOffer(offer.id)} disabled={isSubmitting}>
                    Accept offer
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <p className="empty-state">No lender offers yet. Evaluate an application to see matched options.</p>
          )}
        </section>

        <section className="content-section">
          <div className="section-heading">
            <h2>Active Loans</h2>
          </div>

          {loans.length > 0 ? (
            <div className="loans-list">
              {loans.map((loan) => (
                <div key={loan.id} className="loan-card">
                  <div>
                    <h3>{loan.id.slice(0, 8)}</h3>
                    <p>Principal: {formatCurrency(loan.principal_amount, 'INR')}</p>
                    <p>EMI: {formatCurrency(loan.emi, 'INR')}</p>
                  </div>
                  <div className="repayment-list">
                    {(repayments[loan.id] ?? []).map((repayment) => (
                      <div key={repayment.id} className="repayment-item">
                        <div>
                          <strong>Installment {repayment.installment_number}</strong>
                          <small>{formatDate(repayment.due_date)}</small>
                        </div>
                        <div>
                          <span>{formatCurrency(repayment.amount, 'INR')}</span>
                          <span className={`status status-${repayment.status.toLowerCase()}`}>{repayment.status}</span>
                        </div>
                        <button
                          type="button"
                          className="primary-btn"
                          disabled={isSubmitting || repayment.status === 'PAID'}
                          onClick={() => handlePayRepayment(repayment.id, repayment.amount)}
                        >
                          Pay
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="empty-state">No active loans available yet.</p>
          )}
        </section>
      </main>
    </div>
  )
}
