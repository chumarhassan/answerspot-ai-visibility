import { Gift, Copy, ShareNetwork, Ticket, LinkedinLogo, TwitterLogo } from "@phosphor-icons/react";
import { useEffect, useState } from "react";
import { api } from "../api";
import { Skeleton } from "../components/Skeleton.jsx";
import { useToast } from "../components/Toast.jsx";
export default function Referrals() {
  const toast = useToast();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    (async () => {
      try {
        const data = await api.get("/api/referrals/stats");
        setStats(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    })();
  }, []);
  const getInviteLink = () => `${window.location.origin}/signup?ref=${stats?.code}`;
  function copyCode() {
    navigator.clipboard.writeText(stats.code);
    toast.success("Code copied to clipboard!");
  }
  function copyLink() {
    const url = getInviteLink();
    navigator.clipboard.writeText(url);
    toast.success("Referral link copied!");
  }
  function shareX() {
    const text = encodeURIComponent(`I'm tracking my local business's AI visibility with Answerspot. Check it out! ${getInviteLink()}`);
    window.open(`https://twitter.com/intent/tweet?text=${text}`, "_blank");
  }
  function shareLinkedIn() {
    const url = encodeURIComponent(getInviteLink());
    window.open(`https://www.linkedin.com/sharing/share-offsite/?url=${url}`, "_blank");
  }
  if (loading) return <ReferralsSkeleton />;
  return (
    <>
      <div className="page-head">
        <h1>Invite friends</h1>
        <p className="lead small">Grow Answerspot and unlock premium features for free.</p>
      </div>
      <div className="grid grid-2 stagger">
        <div className="card">
          <div className="card-title"><Gift size={15} weight="bold" /> Your referral code</div>
          <div className="referral-box mt-4">
            <span className="referral-code">{stats.code}</span>
            <button className="icon-btn" onClick={copyCode} title="Copy code"><Copy size={18} /></button>
          </div>
          <p className="muted small mt-6">
            Share this code with your friends. When they sign up, you'll both get credit.
          </p>
          <button className="btn btn-primary btn-block mt-4" onClick={copyLink}>
            <ShareNetwork size={18} weight="bold" /> Copy invite link
          </button>
          <div className="share-row mt-4">
            <button className="btn btn-ghost" onClick={shareX}>
              <TwitterLogo size={18} weight="bold" /> Share
            </button>
            <button className="btn btn-ghost" onClick={shareLinkedIn}>
              <LinkedinLogo size={18} weight="bold" /> Share
            </button>
          </div>
        </div>
        <div className="card">
          <div className="card-title"><Ticket size={15} weight="bold" /> Current progress</div>
          <div className="referral-stats mt-6">
            <div className="stat-big">{stats.count}</div>
            <div className="stat-label">Friends joined</div>
          </div>
          <div className="milestone mt-6">
            <div className="spread small">
              <span>Goal: 3 friends</span>
              <span className={stats.reward_eligible ? "color-good" : ""}>
                {stats.count}/3
              </span>
            </div>
            <div className="progress-bar mt-2">
              <div
                className="progress-fill"
                style={{ width: `${Math.min((stats.count / 3) * 100, 100)}%` }}
              />
            </div>
          </div>
          <p className="muted small mt-4">
            Collect 3 referrals to upgrade to <strong>Starter Plan</strong> for 1 year, free.
          </p>
        </div>
      </div>
    </>
  );
}
function ReferralsSkeleton() {
  return (
    <div aria-busy="true">
      <div className="page-head"><Skeleton width={180} height={26} radius={8} /></div>
      <div className="grid grid-2">
        <div className="card"><Skeleton width="100%" height={140} radius={12} /></div>
        <div className="card"><Skeleton width="100%" height={140} radius={12} /></div>
      </div>
    </div>
  );
}