import { loadStripe, type Stripe } from '@stripe/stripe-js'

let stripePromise: Promise<Stripe | null> | null = null

export const getStripe = () => {
  if (!stripePromise) {
    const publicKey = import.meta.env.VITE_STRIPE_PUBLIC_KEY
    if (!publicKey) {
      console.error('VITE_STRIPE_PUBLIC_KEY missing in env')
    }
    stripePromise = loadStripe(publicKey)
  }
  return stripePromise
}
