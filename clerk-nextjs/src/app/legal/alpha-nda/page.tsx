export default function AlphaNDA() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <div className="bg-white/5 rounded-xl border border-white/10 p-8">
        <h1 className="text-3xl font-bold text-red-500 mb-2">Alpha Non-Disclosure Agreement</h1>
        <p className="text-gray-400 text-sm mb-8 pb-4 border-b border-white/10">
          Effective Date: February 18, 2026 | Version 1.0
        </p>

        <div className="prose prose-invert prose-sm max-w-none space-y-6">
          <div className="bg-red-500/10 border-l-4 border-red-500 p-4 rounded-r">
            <strong>CONFIDENTIALITY NOTICE:</strong> This Agreement creates legally binding
            confidentiality obligations. Violation may result in termination and legal action.
          </div>

          <Section title="1. Confidential Information">
            <p className="text-gray-300">Includes but is not limited to:</p>
            <ul className="list-disc pl-5 space-y-2 text-gray-300">
              <li>All software, code, algorithms, and technical specifications</li>
              <li>Tokenomics details, economic models, and financial projections</li>
              <li>Business strategies, roadmaps, and planned features</li>
              <li>Bug reports, security vulnerabilities, and system weaknesses</li>
              <li>The identities of other Alpha Testers</li>
            </ul>
          </Section>

          <Section title="2. Obligations">
            <ul className="list-disc pl-5 space-y-2 text-gray-300">
              <li><strong>NOT disclose</strong> any Confidential Information to third parties</li>
              <li><strong>NOT post</strong> screenshots or descriptions on social media</li>
              <li><strong>NOT share</strong> your account credentials or invitation codes</li>
              <li><strong>Immediately notify</strong> Foundups of any suspected breach</li>
            </ul>
          </Section>

          <Section title="3. Duration">
            <div className="bg-[#7c5cfc]/10 border-l-4 border-[#7c5cfc] p-4 rounded-r">
              <p>
                Confidentiality obligations remain in effect for <strong>three (3) years</strong> from
                disclosure, or until information becomes publicly available through authorized release.
              </p>
            </div>
          </Section>

          <Section title="4. Governing Law">
            <div className="bg-[#7c5cfc]/10 border-l-4 border-[#7c5cfc] p-4 rounded-r">
              <p>
                This Agreement shall be governed by the laws of <strong>Japan</strong>.
                Any dispute shall be subject to the exclusive jurisdiction of the{" "}
                <strong>Fukui District Court</strong> in Fukui, Japan.
              </p>
            </div>
          </Section>

          <Section title="5. Contact">
            <p>
              <strong>Foundups K.K.</strong><br />
              Email: legal@foundups.com
            </p>
          </Section>
        </div>

        <div className="mt-8 pt-4 border-t border-white/10 text-center">
          <div className="bg-[#7c5cfc]/10 border border-[#7c5cfc]/30 p-4 rounded-lg">
            <p className="text-sm">
              <strong>ACCEPTANCE:</strong> By signing up, you acknowledge that you have read,
              understood, and agree to be bound by this Non-Disclosure Agreement.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div>
      <h2 className="text-lg font-semibold text-[#7c5cfc] mb-3">{title}</h2>
      {children}
    </div>
  );
}
