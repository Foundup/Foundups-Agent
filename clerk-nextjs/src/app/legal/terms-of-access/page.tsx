export default function TermsOfAccess() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <div className="bg-white/5 rounded-xl border border-white/10 p-8">
        <h1 className="text-3xl font-bold text-[#f5a623] mb-2">Alpha Terms of Access</h1>
        <p className="text-gray-400 text-sm mb-8 pb-4 border-b border-white/10">
          Effective Date: February 18, 2026 | Version 1.0
        </p>

        <div className="prose prose-invert prose-sm max-w-none space-y-6">
          <p>
            These Alpha Terms of Access (&quot;Terms&quot;) constitute a legally binding agreement between you
            and <strong>Foundups K.K.</strong>, a company organized under the laws of Japan.
          </p>

          <Section title="1. Eligibility">
            <ul className="list-disc pl-5 space-y-2 text-gray-300">
              <li>Be at least 18 years of age</li>
              <li>Be an individual acting in your personal capacity</li>
              <li><strong>NOT</strong> be an &quot;accredited investor&quot; as defined by SEC regulations</li>
              <li><strong>NOT</strong> be acting as a representative of any company or organization</li>
            </ul>
          </Section>

          <Section title="2. No Investment or Securities">
            <div className="bg-[#7c5cfc]/10 border-l-4 border-[#7c5cfc] p-4 rounded-r">
              <p>
                The Alpha Program does not constitute an offer or sale of securities.
                UPS tokens are utility tokens designed for platform functionality only.
              </p>
            </div>
          </Section>

          <Section title="3. Governing Law">
            <div className="bg-[#7c5cfc]/10 border-l-4 border-[#7c5cfc] p-4 rounded-r">
              <p>
                These Terms shall be governed by the laws of <strong>Japan</strong>.
                Any dispute shall be subject to the exclusive jurisdiction of the{" "}
                <strong>Fukui District Court</strong> in Fukui, Japan.
              </p>
            </div>
          </Section>

          <Section title="4. Contact">
            <p>
              <strong>Foundups K.K.</strong><br />
              Email: legal@foundups.com
            </p>
          </Section>
        </div>

        <div className="mt-8 pt-4 border-t border-white/10 text-center text-sm text-gray-400">
          By signing up, you acknowledge that you have read and agree to these Terms.
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
