// "Continue with Google" — kicks off the OAuth redirect. The client SECRET stays on
// the server; only the public client id is used here.
import { GoogleLogo } from "@phosphor-icons/react";

export default function GoogleButton({ label = "Continue with Google" }) {
  const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;
  const redirectUri = `${window.location.origin}/auth/google/callback`;

  function start() {
    const params = new URLSearchParams({
      client_id: clientId,
      redirect_uri: redirectUri,
      response_type: "code",
      scope: "openid email profile",
      access_type: "online",
      prompt: "select_account",
    });
    window.location.href = `https://accounts.google.com/o/oauth2/v2/auth?${params}`;
  }

  if (!clientId) {
    return (
      <button className="btn btn-ghost btn-block" disabled title="Set VITE_GOOGLE_CLIENT_ID to enable">
        <GoogleLogo size={18} weight="bold" /> {label} (not configured)
      </button>
    );
  }

  return (
    <button className="btn btn-ghost btn-block" onClick={start}>
      <GoogleLogo size={18} weight="bold" /> {label}
    </button>
  );
}
