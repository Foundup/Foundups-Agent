import { currentUser } from "@clerk/nextjs/server";
import { redirect } from "next/navigation";

export default async function MemberPage() {
  const user = await currentUser();

  // This should be caught by middleware, but double-check
  if (!user) {
    redirect("/");
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      {/* Welcome Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">
          Welcome back, {user.firstName || user.emailAddresses[0]?.emailAddress || "Member"}!
        </h1>
        <p className="text-gray-400">Your FoundUPS dashboard</p>
      </div>

      {/* Stats Grid */}
      <div className="grid md:grid-cols-4 gap-4 mb-8">
        {/* UPS Balance with Wallet button */}
        <div className="bg-white/5 rounded-xl border border-white/10 p-4">
          <div className="flex items-center gap-3">
            <span className="text-2xl">💰</span>
            <div>
              <div className="text-2xl font-bold">--</div>
              <div className="text-sm text-gray-400">UPS Balance</div>
            </div>
            <button className="ml-auto px-3 py-1 bg-[#7c5cfc] rounded-lg text-sm font-medium hover:bg-[#6b4ce0] transition">
              Wallet
            </button>
          </div>
        </div>
        {/* My FoundUps with View button */}
        <div className="bg-white/5 rounded-xl border border-white/10 p-4">
          <div className="flex items-center gap-3">
            <span className="text-2xl">🧊</span>
            <div>
              <div className="text-2xl font-bold">0</div>
              <div className="text-sm text-gray-400">My FoundUps</div>
            </div>
            <button className="ml-auto px-3 py-1 bg-[#7c5cfc] rounded-lg text-sm font-medium hover:bg-[#6b4ce0] transition">
              View
            </button>
          </div>
        </div>
        {/* Active Agents with Add button */}
        <div className="bg-white/5 rounded-xl border border-white/10 p-4">
          <div className="flex items-center gap-3">
            <span className="text-2xl">🤖</span>
            <div>
              <div className="text-2xl font-bold">0</div>
              <div className="text-sm text-gray-400">Active Agents</div>
            </div>
            <button className="ml-auto px-3 py-1 bg-[#7c5cfc] rounded-lg text-sm font-medium hover:bg-[#6b4ce0] transition">
              Add
            </button>
          </div>
        </div>
        {/* Invites with inline email input */}
        <div className="bg-white/5 rounded-xl border border-white/10 p-4">
          <div className="flex items-center gap-3 mb-3">
            <span className="text-2xl">🎁</span>
            <div>
              <div className="text-2xl font-bold">5</div>
              <div className="text-sm text-gray-400">Invites Left</div>
            </div>
            <button className="ml-auto px-3 py-1 bg-[#7c5cfc] rounded-lg text-sm font-medium hover:bg-[#6b4ce0] transition">
              Send
            </button>
          </div>
          <input
            type="email"
            placeholder="friend@email.com"
            className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-sm placeholder:text-gray-500 focus:outline-none focus:border-[#7c5cfc]"
          />
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Recent Activity */}
        <div className="bg-white/5 rounded-xl border border-white/10 p-6">
          <h2 className="text-xl font-semibold mb-4">Recent Activity</h2>
          <div className="text-gray-400 text-center py-8">
            <p>No recent activity yet.</p>
            <p className="text-sm mt-2">Start by creating a FoundUP or joining one!</p>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white/5 rounded-xl border border-white/10 p-6">
          <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
          <div className="space-y-3">
            <ActionButton icon="🚀" label="Launch a FoundUP" />
            <ActionButton icon="🔍" label="Explore FoundUps" />
            <ActionButton icon="⭐" label="Upgrade" />
          </div>
        </div>
      </div>

      {/* Coming Soon Notice */}
      <div className="mt-8 p-6 bg-[#7c5cfc]/10 border border-[#7c5cfc]/30 rounded-xl text-center">
        <p className="text-[#7c5cfc] font-medium">
          🚧 Alpha Build — More features coming soon!
        </p>
      </div>
    </div>
  );
}

function StatCard({ icon, label, value }: { icon: string; label: string; value: string }) {
  return (
    <div className="bg-white/5 rounded-xl border border-white/10 p-4">
      <div className="flex items-center gap-3">
        <span className="text-2xl">{icon}</span>
        <div>
          <div className="text-2xl font-bold">{value}</div>
          <div className="text-sm text-gray-400">{label}</div>
        </div>
      </div>
    </div>
  );
}

function ActionButton({ icon, label, disabled = false }: { icon: string; label: string; disabled?: boolean }) {
  return (
    <button
      className={`w-full flex items-center gap-3 p-3 rounded-lg border transition ${
        disabled
          ? "border-white/5 text-gray-500 cursor-not-allowed"
          : "border-white/10 hover:bg-white/5 hover:border-[#7c5cfc]/50"
      }`}
      disabled={disabled}
    >
      <span className="text-xl">{icon}</span>
      <span>{label}</span>
      {disabled && <span className="ml-auto text-xs text-gray-600">Soon</span>}
    </button>
  );
}
