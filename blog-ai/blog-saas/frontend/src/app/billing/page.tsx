"use client";
import { useState, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import { loadStripe } from "@stripe/stripe-js";
import { Elements, PaymentElement, useStripe, useElements } from "@stripe/react-stripe-js";

const stripePromise = loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY || "pk_test_51RuUkA9TXLctvE6F5II8MqzR3cLyyL5CucNV7KS2ouOSmKYuUriJWztRizjdHdVBtTs8CGmYMahqkb13r4xM5NPY002pWVcSka");

const PLAN_NAMES: Record<number, string> = { 2: "Creator — $19/mo", 3: "Brand — $79/mo" };

function CheckoutForm({ planId, onSuccess }: { planId: number; onSuccess: () => void }) {
  const stripe = useStripe();
  const elements = useElements();
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [succeeded, setSucceeded] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!stripe || !elements) return;
    setLoading(true);
    setError(null);

    const { error: submitErr } = await elements.submit();
    if (submitErr) { setError(submitErr.message || "Error"); setLoading(false); return; }

    const { error: confirmErr } = await stripe.confirmPayment({
      elements,
      confirmParams: { return_url: window.location.origin + "/billing/success" },
    });

    if (confirmErr) {
      setError(confirmErr.message || "Payment failed");
      setLoading(false);
    } else {
      setSucceeded(true);
      onSuccess();
    }
  }

  if (succeeded) {
    return (
      <div style={{ textAlign: "center", padding: "3rem" }}>
        <p style={{ fontSize: "1.5rem", color: "#4a9a4a", fontFamily: "Georgia, serif" }}>✓ Subscribed</p>
        <p style={{ color: "#555", fontSize: "0.85rem", marginTop: "0.5rem" }}>Your agents are now active.</p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit}>
      <div style={{ marginBottom: "1.5rem" }}>
        <PaymentElement options={{ layout: "tabs" }} />
      </div>
      {error && <p style={{ color: "#9a4a4a", fontSize: "0.8rem", marginBottom: "1rem", fontFamily: "monospace" }}>{error}</p>}
      <button
        type="submit"
        disabled={!stripe || loading}
        style={{
          width: "100%", padding: "0.875rem",
          background: loading ? "#111" : "#4a7a9a",
          border: "1px solid #4a7a9a",
          color: loading ? "#444" : "#0a0a0a",
          fontFamily: "monospace", fontSize: "0.85rem",
          letterSpacing: "0.1em", textTransform: "uppercase",
          cursor: loading ? "not-allowed" : "pointer",
          transition: "all 0.2s",
        }}
      >
        {loading ? "Processing..." : `Subscribe to ${PLAN_NAMES[planId]}`}
      </button>
      <p style={{ textAlign: "center", marginTop: "1rem", fontSize: "0.7rem", color: "#333", fontFamily: "monospace" }}>
        Test mode — use card 4242 4242 4242 4242
      </p>
    </form>
  );
}

function BillingContent() {
  const { user } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const planId = parseInt(searchParams.get("plan") || "2");

  const [clientSecret, setClientSecret] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [currentSub, setCurrentSub] = useState<any>(null);
  const [loadingPortal, setLoadingPortal] = useState(false);

  useEffect(() => {
    if (!user) { router.push("/login"); return; }

    // Cargar suscripción actual
    fetch("/api/proxy/billing/me", {
      headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
    }).then(r => r.json()).then(d => setCurrentSub(d)).catch(() => {});

    // Si viene con plan, crear payment intent
    if (planId && [2, 3].includes(planId)) {
      fetch("/api/proxy/billing/create-payment-intent", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
        body: JSON.stringify({ plan_id: planId }),
      })
        .then(r => r.json())
        .then(d => {
          if (d.client_secret) setClientSecret(d.client_secret);
          else setError(d.detail || "Error creating payment session");
        })
        .catch(() => setError("Network error"));
    }
  }, [user, planId]);

  async function handleCancel() {
    if (!confirm("Cancel your subscription at end of period?")) return;
    setLoadingPortal(true);
    await fetch("/api/proxy/billing/cancel", {
      method: "POST",
      headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
    });
    setLoadingPortal(false);
    setCurrentSub((s: any) => ({ ...s, status: "canceling" }));
  }

  const stripeOptions = clientSecret ? {
    clientSecret,
    appearance: {
      theme: "night" as const,
      variables: { colorPrimary: "#4a7a9a", colorBackground: "#0d0d0d", colorText: "#e8e0d0", fontFamily: "monospace", borderRadius: "0px" },
    },
  } : null;

  return (
    <div style={{ minHeight: "100vh", background: "#0a0a0a", color: "#e8e0d0", fontFamily: "monospace", padding: "4rem 1rem" }}>
      <div style={{ maxWidth: 480, margin: "0 auto" }}>

        {/* Header */}
        <p style={{ fontSize: "0.65rem", letterSpacing: "0.2em", textTransform: "uppercase", color: "#444", marginBottom: "0.5rem" }}>
          Billing
        </p>
        <h1 style={{ fontSize: "1.75rem", fontFamily: "Georgia, serif", fontWeight: 400, color: "#f0e8d8", margin: "0 0 2rem 0" }}>
          {planId ? PLAN_NAMES[planId] : "Manage subscription"}
        </h1>

        {/* Current sub status */}
        {currentSub && currentSub.plan !== "free" && (
          <div style={{ border: "1px solid #1a1a1a", padding: "1rem 1.25rem", marginBottom: "2rem", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div>
              <p style={{ margin: 0, fontSize: "0.75rem", color: "#555", textTransform: "uppercase", letterSpacing: "0.1em" }}>Current plan</p>
              <p style={{ margin: "0.25rem 0 0", fontSize: "0.9rem", color: "#e8e0d0" }}>{currentSub.plan} — {currentSub.status}</p>
            </div>
            {currentSub.status === "active" && (
              <button onClick={handleCancel} disabled={loadingPortal} style={{ background: "none", border: "1px solid #2a1a1a", color: "#664444", fontFamily: "monospace", fontSize: "0.7rem", padding: "0.4rem 0.75rem", cursor: "pointer", letterSpacing: "0.1em" }}>
                {loadingPortal ? "..." : "Cancel"}
              </button>
            )}
            {currentSub.status === "canceling" && (
              <span style={{ fontSize: "0.7rem", color: "#664444" }}>Cancels at period end</span>
            )}
          </div>
        )}

        {/* Checkout */}
        {error && <p style={{ color: "#9a4a4a", fontSize: "0.85rem", marginBottom: "1.5rem" }}>{error}</p>}

        {clientSecret && stripeOptions ? (
          <Elements stripe={stripePromise} options={stripeOptions}>
            <CheckoutForm planId={planId} onSuccess={() => router.push("/pricing")} />
          </Elements>
        ) : !error && planId && (
          <div style={{ color: "#333", fontSize: "0.8rem", padding: "2rem 0" }}>Loading payment form...</div>
        )}

        {/* Back */}
        <div style={{ marginTop: "2rem", borderTop: "1px solid #111", paddingTop: "1.5rem" }}>
          <a href="/pricing" style={{ color: "#444", fontSize: "0.75rem", textDecoration: "none", letterSpacing: "0.1em" }}>← Back to pricing</a>
        </div>
      </div>
    </div>
  );
}

export default function BillingPage() {
  return <Suspense fallback={<div style={{ background: "#0a0a0a", minHeight: "100vh" }} />}><BillingContent /></Suspense>;
}
