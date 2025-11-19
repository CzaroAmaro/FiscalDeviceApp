import api from './index'

export interface CreateSessionResp {
  sessionId?: string
  url?: string
  orderId?: string
  error?: string
}

export const createCheckoutSession = async (amountCents?: number): Promise<CreateSessionResp> => {
  const payload: any = {}
  if (amountCents) payload.amount_cents = amountCents
  const res = await api.post<CreateSessionResp>('/create-checkout-session/', payload)
  return res.data
}

export const handlePaymentSuccess = async (sessionId: string) => {
  const res = await api.post('/handle-payment-success/', { session_id: sessionId })
  return res.data
}

export const redeemActivationCode = async (code: string) => {
  const res = await api.post('/redeem-activation-code/', { code })
  return res.data
}

export const myActivationCodes = async () => {
  const res = await api.get('/my-activation-codes/')
  return res.data
}
