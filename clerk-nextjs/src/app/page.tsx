import { SignInButton, SignUpButton, SignedIn, SignedOut } from "@clerk/nextjs";
import Link from "next/link";

export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[80vh] px-4">
      {/* Hero */}
      <div className="text-center max-w-2xl">
        <h1 className="text-5xl font-bold mb-6">
          Found<span className="text-[#7c5cfc]">UPS</span>
        </h1>
        <p className="text-xl text-gray-400 mb-8">
          Peer-to-Peer Autonomous Venture System
        </p>

        <SignedOut>
          <div className="flex gap-4 justify-center">
            <SignInButton mode="modal">
              <button className="px-6 py-3 border border-[#7c5cfc] text-[#7c5cfc] rounded-lg hover:bg-[#7c5cfc]/10 transition">
                Sign In
              </button>
            </SignInButton>
            <SignUpButton mode="modal">
              <button className="px-6 py-3 bg-[#7c5cfc] rounded-lg hover:bg-[#6b4ce0] transition font-medium">
                ENTER →
              </button>
            </SignUpButton>
          </div>
          <p className="mt-4 text-sm text-gray-500">
            By signing up, you agree to the{" "}
            <a href="/legal/terms-of-access" className="text-[#7c5cfc] hover:underline">
              Terms of Access
            </a>{" "}
            and{" "}
            <a href="/legal/alpha-nda" className="text-[#7c5cfc] hover:underline">
              NDA
            </a>
          </p>
        </SignedOut>

        <SignedIn>
          <Link
            href="/member"
            className="inline-block px-8 py-4 bg-[#7c5cfc] rounded-lg hover:bg-[#6b4ce0] transition font-medium text-lg"
          >
            Go to Dashboard →
          </Link>
        </SignedIn>
      </div>

      {/* Features */}
      <div className="grid md:grid-cols-3 gap-6 mt-20 max-w-4xl">
        <div className="p-6 bg-white/5 rounded-xl border border-white/10">
          <div className="text-3xl mb-3">🔗</div>
          <h3 className="font-semibold mb-2">BTC-Native</h3>
          <p className="text-sm text-gray-400">UPS tokens backed by Bitcoin. No speculation, pure utility.</p>
        </div>
        <div className="p-6 bg-white/5 rounded-xl border border-white/10">
          <div className="text-3xl mb-3">🤖</div>
          <h3 className="font-semibold mb-2">Agent-Powered</h3>
          <p className="text-sm text-gray-400">AI agents do the work. Humans guide the vision.</p>
        </div>
        <div className="p-6 bg-white/5 rounded-xl border border-white/10">
          <div className="text-3xl mb-3">🌊</div>
          <h3 className="font-semibold mb-2">Tide Economics</h3>
          <p className="text-sm text-gray-400">Cooperative ecosystem. All FoundUps rise together.</p>
        </div>
      </div>
    </div>
  );
}
