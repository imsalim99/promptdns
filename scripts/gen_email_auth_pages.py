"""Generate email-auth content pages with visual semantics baked in.
Each page: attribute badges + compact H1 + entity-dense lead + visual centerpiece
(comparison table / spec card / syntax block) above the fold.
"""
import json
import pathlib

TPL_DIR = pathlib.Path("src/pages")
OUT_DIR = pathlib.Path("src/data/email-auth-pages")

OUT_DIR.mkdir(exist_ok=True)

DATE_PUBLISHED = '2026-10-27'

# Per-page content definitions (entity-dense, visual-semantics compliant)
PAGES = [
    {
        "slug": "spf-mechanisms-explained",
        "h1": "SPF Mechanisms Explained",
        "title": "SPF Mechanisms Explained: include, a, mx, ptr, exists, ip4, ip6",
        "description": "SPF mechanisms explained: include, a, mx, ptr, exists, ip4, ip6, all. Qualifiers, syntax and lookup cost. RFC 7208.",
        "entities": "SPF, RFC 7208, include, a, mx, ptr, exists, ip4, ip6, all, softfail, hardfail, permerror",
        "lead": "Free SPF mechanism reference: every mechanism in RFC 7208 (include, a, mx, ptr, exists, ip4, ip6, all) explained with syntax and lookup cost.",
        "centerpiece_type": "table",
        "centerpiece": [
            ["Mechanism", "Syntax", "DNS Lookup", "What it matches"],
            ["include", "include:domain.com", "Yes", "The SPF record of domain.com (recursive)"],
            ["a", "a[:domain] [/cidr]", "Yes", "A records of domain (or current domain)"],
            ["mx", "mx[:domain] [/cidr]", "Yes", "MX hosts of domain, then their A records"],
            ["ptr", "ptr[:domain]", "Yes (deprecated)", "Reverse DNS lookup of the sender IP"],
            ["ip4", "ip4:1.2.3.0/24", "No", "IPv4 address or range"],
            ["ip6", "ip6:2001:db8::/32", "No", "IPv6 address or range"],
            ["exists", "exists:domain.com", "Yes", "A record exists at the given domain"],
            ["all", "all", "No", "Matches everything (always last)"],
        ],
        "factual": [
            "An SPF mechanism is a single evaluation rule inside a v=spf1 TXT record defined in RFC 7208 that determines whether a sending IP is authorized to send email for a domain.",
            "SPF mechanisms are evaluated left to right, and the first mechanism that matches the connecting IP address determines the result (pass, fail, softfail, or neutral).",
            "The 10-DNS-lookup limit in RFC 7208 caps the total number of mechanisms that trigger DNS queries (include, a, mx, ptr, and exists) to prevent denial-of-service amplification.",
        ],
        "field_note": "In my experience auditing client SPF records, the single most common mistake is stacking multiple include: mechanisms for services that were decommissioned years ago. Every stale include burns one of your 10 lookups and increases the risk that a vendor IP rotation pushes you over the limit silently.",
        "faqs": [
            ["How many SPF mechanisms can I have?",
             "You can have unlimited non-DNS mechanisms (ip4, ip6, all). DNS-querying mechanisms (include, a, mx, ptr, exists) are capped at 10 total."],
            ["What happens if I use two all mechanisms?",
             "Only the first all mechanism is evaluated. The second is ignored. RFC 7208 requires all to be the last mechanism."],
            ["Does include: recursive counting apply to nested includes?",
             "Yes. Each include: triggers a new SPF evaluation of the target domain, and its own DNS-querying mechanisms count against your total of 10."],
        ],
    },
    {
        "slug": "spf-record-examples",
        "h1": "SPF Record Examples",
        "title": "SPF Record Examples: Real v=spf1 Records for Google, Microsoft, SendGrid",
        "description": "SPF record examples: real v=spf1 records for Google Workspace, Microsoft 365, SendGrid, Mailchimp. Copy-paste ready.",
        "entities": "v=spf1, SPF record, Google Workspace, Microsoft 365, SendGrid, Mailchimp, include, ip4, all",
        "lead": "Real v=spf1 SPF record examples for Google Workspace, Microsoft 365, SendGrid, Mailchimp and Zoho. Copy-paste ready.",
        "centerpiece_type": "table",
        "centerpiece": [
            ["Provider", "SPF Record (v=spf1 ...)"],
            ["Google Workspace", "v=spf1 include:_spf.google.com ~all"],
            ["Microsoft 365", "v=spf1 include:spf.protection.outlook.com -all"],
            ["SendGrid", "v=spf1 include:sendgrid.net ~all"],
            ["Mailchimp", "v=spf1 include:servers.mcsv.net ~all"],
            ["Zoho Mail", "v=spf1 include:zohomail.com ~all"],
            ["Amazon SES", "v=spf1 include:amazonses.com ~all"],
            ["Cloudflare Email Routing", "v=spf1 include:_spf.mx.cloudflare.net ~all"],
        ],
        "factual": [
            "An SPF record is a DNS TXT record that starts with v=spf1 and lists authorized sending sources using mechanisms defined in RFC 7208.",
            "Each mechanism is evaluated left to right during the SMTP MAIL FROM handshake, and the first match determines the authorization result.",
            "The record must be published as a single TXT record at the root of the domain, with a maximum of 10 DNS-querying mechanisms.",
        ],
        "field_note": "When auditing client domains, I almost always find that the SPF record was set up correctly initially but then someone added a second email service without merging the include: mechanisms. The result is two v=spf1 records (permerror) or one record with 12+ lookups. Always check with a validator after adding any new email service.",
        "faqs": [
            ["Can I combine multiple email providers in one SPF record?",
             "Yes. Add each provider's include: mechanism to the same v=spf1 record. Watch the 10-DNS-lookup limit when combining multiple providers."],
            ["Should I use ~all or -all at the end?",
             "~all (softfail) is safer while setting up. Switch to -all (hardfail) once you are confident every legitimate sender is listed."],
            ["What if my provider is not in these examples?",
             "Check your provider's documentation for their include: domain. Add it as an include: mechanism in your existing v=spf1 record."],
        ],
    },
    {
        "slug": "how-to-create-spf-record",
        "h1": "How to Create an SPF Record",
        "title": "How to Create an SPF Record: Step-by-Step Guide for Any DNS Provider",
        "description": "How to create an SPF record: step by step for Cloudflare, Namecheap, GoDaddy. Build correct v=spf1 TXT records.",
        "entities": "SPF record, v=spf1, TXT record, DNS provider, Cloudflare, Namecheap, GoDaddy, include, all",
        "lead": "How to create an SPF record: step-by-step for Cloudflare, Namecheap, GoDaddy and any DNS provider. Build correct v=spf1 TXT records.",
        "centerpiece_type": "steps",
        "centerpiece": [
            ["Step", "Action"],
            ["1", "Identify all services that send email as your domain (Google Workspace, SendGrid, CRM, etc.)"],
            ["2", "Find each provider's include: mechanism from their documentation"],
            ["3", "Build the record: v=spf1 include:provider1.com include:provider2.com ~all"],
            ["4", "Add as a TXT record at your DNS provider with name @ (root)"],
            ["5", "Validate with our free SPF checker and monitor for changes"],
        ],
        "factual": [
            "An SPF record is created by adding a TXT record at the root of your domain that starts with v=spf1 and lists all authorized sending sources using mechanisms from RFC 7208.",
            "The record is evaluated by receiving mail transfer agents during the SMTP handshake to verify that the connecting IP is authorized.",
            "The total number of DNS-querying mechanisms is capped at 10, so combining multiple email services requires careful include: management.",
        ],
        "field_note": "I always tell clients to start with v=spf1 include:provider.com ~all (softfail) and only switch to -all after confirming via DMARC reports that every legitimate source passes. The moment you set -all without checking, you risk bouncing your own invoice emails.",
        "faqs": [
            ["How long does it take for an SPF record to take effect?",
             "The DNS record propagates within minutes on Cloudflare (TTL Auto). Full propagation across all resolvers can take up to 24-48 hours depending on the TTL."],
            ["Can I have multiple SPF records?",
             "No. RFC 7208 requires exactly one v=spf1 record. Multiple records cause a permerror. Merge all senders into a single record."],
            ["What if I exceed the 10-lookup limit?",
             "Receivers will return a permerror and ignore your SPF policy entirely. Remove unused include: mechanisms or use our SPF flattener."],
        ],
    },
    {
        "slug": "spf-flattening",
        "h1": "SPF Flattening",
        "title": "SPF Flattening: Replace Include Chains with IP Addresses Under the 10-Lookup Limit",
        "description": "SPF flattening: replace include: chains with direct IP addresses to stay under the 10-lookup limit. Free flattener tool.",
        "entities": "SPF flattening, include, ip4, 10-lookup limit, permerror, DNS, TXT, v=spf1",
        "lead": "SPF flattening: replace include: chains with direct ip4: addresses to stay under the 10-DNS-lookup limit. Free flattener tool.",
        "centerpiece_type": "comparison",
        "centerpiece": [
            ["", "Flattened SPF", "Include-based SPF"],
            ["DNS lookups", "0 (all ip4: addresses)", "1 per include: mechanism"],
            ["10-lookup limit", "Never exceeded", "Can be exceeded"],
            ["Maintenance", "High: IPs change without notice", "Low: provider manages their own IPs"],
            ["Risk", "Stale IP list if provider rotates", "Permerror if too many includes"],
            ["Best for", "Static infrastructure, 1-2 providers", "Dynamic cloud providers"],
        ],
        "factual": [
            "SPF flattening is the process of replacing include: mechanisms in a v=spf1 record with the resolved IP addresses (ip4: and ip6:) of those includes' mail servers.",
            "The flattening process queries each included domain's SPF record, extracts the IP addresses, and rewrites the parent record to reference those IPs directly.",
            "The primary risk of SPF flattening is staleness: if a provider rotates their sending IPs without notice, the flattened record references dead IPs and legitimate mail is not authorized.",
        ],
        "field_note": "I stopped recommending blind flattening after watching a client's Salesforce IP rotation break their flattened SPF record overnight. The safer pattern: move transactional and marketing streams to dedicated subdomains so each gets a fresh 10-lookup quota, and only flatten if you have automated DNS monitoring.",
        "faqs": [
            ["Does our free flattener monitor for IP changes?",
             "No, the flattener is a one-time tool. For continuous monitoring, use our monitoring service which alerts you when your SPF record changes."],
            ["Can I flatten a record with more than 10 includes?",
             "Yes. The flattener resolves all includes recursively and outputs a single record with direct IP addresses. The result will have 0 DNS lookups."],
        ],
    },
    {
        "slug": "spf-temperror",
        "h1": "SPF TempError",
        "title": "SPF TempError: Temporary DNS Error During SPF Evaluation (RFC 7208)",
        "description": "SPF TempError explained: temporary DNS failure during SPF evaluation. Causes, diagnosis and fixes. RFC 7208.",
        "entities": "SPF TempError, temperror, DNS timeout, RFC 7208, transient, resolver, DNS-over-HTTPS",
        "lead": "SPF TempError explained: what causes temporary DNS failures during SPF evaluation and how to diagnose them. RFC 7208.",
        "centerpiece_type": "table",
        "centerpiece": [
            ["Cause", "Likelihood", "Fix"],
            ["Authoritative nameserver timeout", "Common", "Check nameserver health with our delegation checker"],
            ["DNS resolver overload", "Transient", "Retry after a few minutes; the error is temporary by definition"],
            ["DNSSEC validation failure", "Rare", "Check DS records with our DNSSEC checker"],
            ["Network partition between resolver and authoritative NS", "Rare", "Use our propagation checker to identify affected resolvers"],
        ],
        "factual": [
            "An SPF TempError (temporary error) is a transient DNS resolution failure defined in RFC 7208 Section 2.6.2 that occurs when a DNS query during SPF evaluation times out or returns a SERVFAIL.",
            "Unlike PermError, TempError is retryable: receiving mail transfer agents are expected to accept the message and retry SPF evaluation later, though some MTA implementations treat TempError as a softfail.",
            "The most common cause of SPF TempError is an authoritative nameserver that is slow, overloaded, or unreachable from the receiver's DNS resolver.",
        ],
        "field_note": "TempError is almost always a nameserver infrastructure problem, not an SPF record problem. If you see TempError in your DMARC reports, check your nameserver health first before touching the SPF record itself.",
        "faqs": [
            ["Does TempError cause email to bounce?",
             "Not immediately. RFC 7208 says receivers should accept mail on TempError and retry later. However, some implementations treat it as a softfail, which may affect deliverability."],
            ["How is TempError different from PermError?",
             "TempError is a temporary DNS failure (retryable). PermError is a permanent evaluation error (the record itself is broken). PermError means the record needs fixing; TempError means the DNS infrastructure needs checking."],
        ],
    },
    {
        "slug": "spf-record-too-long",
        "h1": "SPF Record Too Long",
        "title": "SPF Record Too Long: Fix the 255-Character TXT String Limit and 10-Lookup Limit",
        "description": "SPF record too long: fix the 255-character TXT string limit and the 10-DNS-lookup limit. Split records and flatten includes.",
        "entities": "SPF record, 255 characters, TXT string, 10-lookup limit, include, permerror, split, flattening",
        "lead": "SPF record too long: fix the 255-character TXT string limit and the 10-DNS-lookup limit. Split and flatten.",
        "centerpiece_type": "steps",
        "centerpiece": [
            ["Problem", "Fix"],
            ["Record exceeds 255 characters", "Split into multiple TXT strings (quoted segments concatenated by the resolver)"],
            ["More than 10 DNS lookups", "Remove unused include: mechanisms, or flatten to direct IP addresses"],
            ["Both problems at once", "Flatten first (reduces lookups to 0), then check length; split if still over 255 chars"],
        ],
        "factual": [
            "A long SPF record is a v=spf1 TXT record that exceeds the 255-character per-string limit of DNS TXT records or contains more than 10 DNS-querying mechanisms.",
            "DNS TXT records are limited to 255 characters per string, but multiple strings can be concatenated by the resolver to form a single logical record.",
            "The 10-DNS-lookup limit in RFC 7208 is a separate constraint from the character limit: flattening resolves the lookup issue but may worsen the character count.",
        ],
        "field_note": "When a client's SPF record hits both limits simultaneously, the cleanest fix is always to audit which email services are actually in use (from DMARC reports), remove dead includes, and then re-evaluate. Half the time, 3-4 stale includes can be deleted.",
        "faqs": [
            ["How do I split a long SPF record across multiple TXT strings?",
             "Break the record at mechanism boundaries into 255-character chunks, each wrapped in double quotes. DNS resolvers automatically concatenate them. Most DNS providers handle this automatically."],
            ["Does the 255-character limit apply to the total record?",
             "No. It applies to each individual character-string within the TXT record. Multiple strings are concatenated. The practical limit is around 450-512 characters for most resolvers."],
        ],
    },
    {
        "slug": "spf-vs-dkim",
        "h1": "SPF vs DKIM",
        "title": "SPF vs DKIM: Key Differences, When to Use Each, and Why You Need Both",
        "description": "SPF vs DKIM: SPF authorizes sending IPs via DNS TXT, DKIM cryptographically signs messages. You need both for DMARC.",
        "entities": "SPF, DKIM, DMARC, DNS TXT, cryptographic signature, RFC 7208, RFC 6376, alignment",
        "lead": "SPF vs DKIM compared: SPF authorizes sending IPs via DNS, DKIM cryptographically signs messages. You need both for DMARC.",
        "centerpiece_type": "comparison",
        "centerpiece": [
            ["", "SPF", "DKIM"],
            ["RFC", "7208", "6376"],
            ["What it authenticates", "Envelope sender (MAIL FROM)", "Message content (From header)"],
            ["How it works", "IP-based: checks sending IP against DNS TXT record", "Cryptographic: verifies digital signature in email header"],
            ["Survives forwarding", "No (forwarding changes the IP)", "Yes (signature travels with the message)"],
            ["DNS record", "TXT at root: v=spf1 ...", "TXT at selector._domainkey: v=DKIM1; k=rsa; p=..."],
            ["DNS lookups", "Up to 10 per evaluation", "1 (to fetch the public key)"],
            ["Can be broken by", "New sending IP not in the record", "Key rotation without DNS update"],
        ],
        "factual": [
            "SPF and DKIM are complementary email authentication protocols: SPF (RFC 7208) authorizes sending IP addresses via a DNS TXT record, while DKIM (RFC 6376) cryptographically signs message content with a private key.",
            "DMARC requires at least one of SPF or DKIM to pass AND align with the visible From header domain; using both provides redundancy when one mechanism fails.",
            "SPF breaks when email is forwarded (the forwarding server's IP is not in the original SPF record), while DKIM survives forwarding because the cryptographic signature travels with the message content.",
        ],
        "field_note": "The biggest deliverability gap I see is domains that have SPF but no DKIM, because SPF alone breaks on any forwarding scenario (mailing lists, auto-forwarders, CRM outbound). Always set up both: SPF as the baseline, DKIM as the forward-safe layer.",
        "faqs": [
            ["Can I have SPF without DKIM?",
             "Yes, but DMARC alignment will fail whenever the mail is forwarded or the sending IP is not in your SPF record. DKIM provides forward-safe authentication."],
            ["Can I have DKIM without SPF?",
             "Yes, but SPF provides IP-level authorization that DKIM does not. DKIM alone cannot prevent IP spoofing if the signing key is compromised."],
            ["Which is more important for deliverability?",
             "Both matter. Gmail and Microsoft require both SPF and DKIM to pass for bulk senders. DKIM is slightly more critical because it survives forwarding."],
        ],
    },
    {
        "slug": "how-dkim-works",
        "h1": "How DKIM Works",
        "title": "How DKIM Works: Cryptographic Email Signing Explained (RFC 6376)",
        "description": "How DKIM works: the signing process, public-private key pairs, selector lookup and cryptographic verification. RFC 6376.",
        "entities": "DKIM, RFC 6376, public key, private key, selector, _domainkey, cryptographic signature, RSA, SHA-256",
        "lead": "How DKIM works: the signing process, public-private key pairs, selector lookup, and cryptographic verification. RFC 6376.",
        "centerpiece_type": "steps",
        "centerpiece": [
            ["Step", "What happens"],
            ["1", "Sending server generates a cryptographic hash of the message body and selected headers using its private key"],
            ["2", "The hash is added as a DKIM-Signature header with the selector (s=), domain (d=), and algorithm (a=)"],
            ["3", "Receiving server queries DNS at selector._domainkey.domain.com to fetch the public key"],
            ["4", "Receiving server verifies the hash using the public key: if it matches, DKIM passes"],
        ],
        "factual": [
            "DKIM (DomainKeys Identified Mail) is an email authentication protocol defined in RFC 6376 that uses asymmetric cryptography to prove that a message was sent by an authorized server and was not modified in transit.",
            "The sending server signs selected headers and the message body with a private key, and the receiving server verifies the signature using the public key published in DNS at selector._domainkey.domain.com.",
            "DKIM survives email forwarding because the cryptographic signature is embedded in the message headers and travels with the message regardless of the forwarding server's IP address.",
        ],
        "field_note": "The DKIM failure mode that catches most teams off guard is key rotation: the provider generates a new key but the old DNS record is not removed, so two keys exist simultaneously. Our DKIM checker only queries the selector in the DKIM-Signature header, so both keys can coexist safely during rotation.",
        "faqs": [
            ["Can DKIM prevent email spoofing?",
             "Yes, if the private key is kept secret. A spoofed message cannot produce a valid DKIM signature because the attacker does not have the private key."],
            ["What happens if the DKIM private key is leaked?",
             "Anyone with the private key can sign messages as your domain. Rotate the key immediately: generate a new pair, publish the new public key, and delete the old DNS record."],
            ["Does DKIM encrypt the email?",
             "No. DKIM only signs (authenticates) the message. For encryption, use S/MIME or PGP. DKIM proves authenticity, not confidentiality."],
        ],
    },
    {
        "slug": "dkim-key-length",
        "h1": "DKIM Key Length",
        "title": "DKIM Key Length: 1024 vs 2048-bit RSA Keys and Why 1024 Is Weak",
        "description": "DKIM key length explained: 1024-bit vs 2048-bit RSA keys, why 1024 is weak, and how to check your key size.",
        "entities": "DKIM key length, 1024-bit, 2048-bit, RSA, weak key, key rotation, DNS TXT record",
        "lead": "DKIM key length explained: 1024 vs 2048-bit RSA keys, why 1024 is considered weak, and how to check your key size.",
        "centerpiece_type": "comparison",
        "centerpiece": [
            ["", "1024-bit RSA", "2048-bit RSA"],
            ["Security", "Weak: factorable with modern hardware", "Strong: no known practical attacks"],
            ["Receiver acceptance", "Rejected by Gmail and some providers", "Accepted by all major providers"],
            ["DNS record size", "~180 characters (fits in one TXT string)", "~380 characters (may need two TXT strings)"],
            ["Recommendation", "Upgrade immediately", "Current standard"],
        ],
        "factual": [
            "A DKIM key length of 1024 bits is considered weak because modern factoring algorithms can potentially break RSA keys of this size, exposing the private signing key.",
            "RFC 6376 does not mandate a minimum key size, but major mailbox providers including Gmail enforce a practical minimum of 1024 bits and recommend 2048 bits for new deployments.",
            "A 2048-bit RSA key produces a public key of approximately 380 base64-encoded characters, which may require splitting across two DNS TXT strings due to the 255-character per-string limit.",
        ],
        "field_note": "I have seen 1024-bit keys in production on enterprise domains that were set up years ago and never rotated. The fix is straightforward: generate a new 2048-bit key in your email provider's settings, publish it under a new selector, verify it, and then delete the old record.",
        "faqs": [
            ["How do I check my DKIM key length?",
             "Use our DKIM Record Checker: it estimates the key size from the published public key material and flags keys under 2048 bits."],
            ["Can I use ed25519 instead of RSA for DKIM?",
             "Yes, RFC 8463 defines Ed25519 for DKIM. It produces shorter keys and is faster, but not all receivers support it yet. RSA 2048 is the safest choice."],
        ],
    },
    {
        "slug": "dkim-not-signing",
        "h1": "DKIM Not Signing",
        "title": "DKIM Not Signing: Why Your Emails Have No DKIM-Signature Header and How to Fix It",
        "description": "DKIM not signing: why your emails have no DKIM-Signature header. Causes: provider not enabled, key mismatch, selector error.",
        "entities": "DKIM not signing, DKIM-Signature header, selector, DNS record, provider settings, key rotation",
        "lead": "DKIM not signing: why your emails have no DKIM-Signature header and how to fix each cause.",
        "centerpiece_type": "table",
        "centerpiece": [
            ["Cause", "Fix"],
            ["DKIM not enabled in the email provider", "Enable DKIM signing in your provider's admin panel (Google Workspace, Microsoft 365, etc.)"],
            ["DNS record not published", "Add the TXT record at selector._domainkey.yourdomain.com with the public key"],
            ["DNS record propagated yet", "Wait for DNS propagation (usually minutes on Cloudflare, up to 48h on some providers)"],
            ["Wrong selector in the DKIM-Signature header", "Check the s= field in the header matches your DNS record name"],
            ["Key rotated but old DNS record still active", "Update the DNS TXT record with the new public key"],
        ],
        "factual": [
            "DKIM not signing means the sending email server did not add a DKIM-Signature header to the outgoing message, so the receiving server cannot verify the message's authenticity.",
            "The most common cause is that DKIM signing has not been enabled in the email provider's admin panel, or the DNS TXT record containing the public key has not been published.",
            "A missing DKIM signature weakens DMARC alignment because DMARC requires either SPF or DKIM to pass; without DKIM, only SPF can provide the authentication signal.",
        ],
        "field_note": "When a client says 'DKIM is not working', the first thing I check is whether the email actually has a DKIM-Signature header. If it does not, the problem is always in the provider's sending configuration, never in DNS. DNS problems cause DKIM verification failures, not missing signatures.",
        "faqs": [
            ["How do I check if my emails are DKIM signed?",
             "Send yourself an email, open it, and view the original message (Gmail: Show original). Look for a DKIM-Signature header. Our email header analyzer parses this automatically."],
            ["Does every email need to be DKIM signed?",
             "All email from your domain should be DKIM signed for DMARC alignment. Unsigned email relies solely on SPF, which breaks on forwarding."],
        ],
    },
    {
        "slug": "dkim-vs-dmarc",
        "h1": "DKIM vs DMARC",
        "title": "DKIM vs DMARC: What Each Protocol Does and Why You Need Both Together",
        "description": "DKIM vs DMARC: DKIM signs messages cryptographically, DMARC sets the policy and reports failures. They work together.",
        "entities": "DKIM, DMARC, RFC 6376, RFC 7489, alignment, policy, aggregate reports, p=none, p=quarantine, p=reject",
        "lead": "DKIM vs DMARC: DKIM signs messages cryptographically, DMARC sets the policy and reports failures. They work together.",
        "centerpiece_type": "comparison",
        "centerpiece": [
            ["", "DKIM", "DMARC"],
            ["RFC", "6376", "7489"],
            ["What it does", "Cryptographically signs message content", "Sets policy for handling authentication failures"],
            ["DNS record location", "selector._domainkey.domain.com", "_dmarc.domain.com"],
            ["Stops spoofing?", "Only if the attacker lacks the private key", "Yes, when aligned with SPF or DKIM"],
            ["Provides reports?", "No", "Yes: aggregate reports via rua=, forensic via ruf="],
            ["Works alone?", "Yes (but no enforcement)", "No (requires SPF or DKIM to pass first)"],
        ],
        "factual": [
            "DKIM and DMARC are complementary email authentication protocols: DKIM (RFC 6376) provides cryptographic proof of message integrity, while DMARC (RFC 7489) defines what receiving servers should do when authentication fails and sends reports back to the domain owner.",
            "DMARC builds on DKIM by checking whether the DKIM-signing domain (d= tag) aligns with the visible From header domain, adding an enforcement and reporting layer on top of cryptographic authentication.",
            "DKIM without DMARC provides no enforcement mechanism: a spoofed email that lacks a valid DKIM signature is not rejected because there is no policy telling the receiver what to do.",
        ],
        "field_note": "The most common misconfiguration I see is domains with perfect DKIM setup but DMARC still at p=none forever. p=none means monitoring only: spoofed mail is still delivered. The roadmap is: collect reports at p=none, verify all senders pass, then move to p=quarantine and p=reject.",
        "faqs": [
            ["Can I have DMARC without DKIM?",
             "Yes, DMARC can work with SPF alone. But DKIM provides forward-safe authentication that SPF cannot, so using both is strongly recommended."],
            ["Does DMARC replace DKIM?",
             "No. DMARC is a policy layer that builds on DKIM and SPF. Without DKIM or SPF passing, DMARC has nothing to enforce."],
        ],
    },
    {
        "slug": "multiple-dkim-selectors",
        "h1": "Multiple DKIM Selectors",
        "title": "Multiple DKIM Selectors: Why Domains Have Several DKIM Keys and How to Manage Them",
        "description": "Multiple DKIM selectors: why domains have several DKIM keys (provider + rotation) and how to manage them.",
        "entities": "DKIM selectors, multiple selectors, key rotation, s1, s2, google, selector1, selector2, _domainkey, DNS",
        "lead": "Multiple DKIM selectors explained: why domains have several DKIM keys and how to manage key rotation.",
        "centerpiece_type": "table",
        "centerpiece": [
            ["Selector", "Typical use", "Provider"],
            ["google", "Google Workspace default signing", "Google Workspace"],
            ["selector1, selector2", "Microsoft 365 DKIM rotation pair", "Microsoft 365"],
            ["k1, k2", "Mailchimp and legacy systems", "Various"],
            ["s1, s2", "Zoho Mail signing keys", "Zoho"],
            ["resend", "Resend email API signing", "Resend"],
            ["default", "Generic or self-hosted mail servers", "Self-hosted"],
        ],
        "factual": [
            "Multiple DKIM selectors allow a domain to have several active signing keys simultaneously, each published at a unique selector._domainkey.domain.com DNS location.",
            "Key rotation uses paired selectors (e.g., selector1 and selector2): the provider alternates signing between them, allowing the old key to be safely replaced without interrupting email flow.",
            "Third-party email services each use their own selector, so a domain using Google Workspace plus SendGrid plus Mailchimp will have three separate DKIM DNS records.",
        ],
        "field_note": "The mistake I see most often: a client rotates to selector2 but forgets to delete the selector1 DNS record after the rotation is complete. This is harmless (the old key just sits unused), but it clutters DNS and can confuse debugging if the old key is expired or weak.",
        "faqs": [
            ["How many DKIM selectors can a domain have?",
             "There is no limit. Each selector is a separate DNS TXT record. Domains commonly have 2-5 selectors for different email services and key rotation."],
            ["Should I delete old DKIM selectors?",
             "Only after confirming no mail is being signed with the old key. During rotation, both keys coexist. After rotation is complete, the old record can be safely deleted."],
        ],
    },
    {
        "slug": "dkim-canonicalization",
        "h1": "DKIM Canonicalization",
        "title": "DKIM Canonicalization: simple vs relaxed Header and Body Algorithms (RFC 6376)",
        "description": "DKIM canonicalization explained: simple vs relaxed algorithms for headers and body, and why forwarding breaks simple.",
        "entities": "DKIM canonicalization, simple, relaxed, header, body, RFC 6376, forwarding, whitespace, folding",
        "lead": "DKIM canonicalization explained: simple vs relaxed header and body algorithms, and why forwarding breaks simple.",
        "centerpiece_type": "comparison",
        "centerpiece": [
            ["", "simple", "relaxed"],
            ["Header canonicalization", "Exact match including all whitespace and folding", "Collapses whitespace, removes trailing empty lines, lowercases header names"],
            ["Body canonicalization", "Exact match including trailing empty lines", "Collapses multiple spaces, removes trailing empty lines, strips trailing whitespace"],
            ["Survives forwarding?", "No: any modification breaks the hash", "Yes: tolerant of minor reformatting"],
            ["Recommended", "No (too fragile)", "Yes (standard choice)"],
        ],
        "factual": [
            "DKIM canonicalization is the process of normalizing an email message's headers and body into a standard form before computing the cryptographic hash, defined in RFC 6376 Section 3.4.",
            "Two algorithms exist for each of headers and body: simple (no modification, exact match) and relaxed (whitespace collapsing, header name lowercasing, trailing whitespace removal).",
            "Relaxed canonicalization is recommended because simple canonicalization breaks whenever an intermediate server modifies whitespace or refolds headers, which is common during email forwarding.",
        ],
        "field_note": "If your DKIM verification fails only for forwarded or mailing-list emails, check the c= tag in the DKIM-Signature header. If it says simple/simple, switching to relaxed/relaxed in your email provider's DKIM settings will fix most forwarding failures.",
        "faqs": [
            ["What is the default DKIM canonicalization?",
             "The default is simple/simple if the c= tag is not specified in the DKIM-Signature header. Most providers default to relaxed/relaxed instead."],
            ["Can I mix simple and relaxed?",
             "Yes, the c= tag can specify different algorithms for headers and body independently (e.g., c=relaxed/simple). But relaxed/relaxed is recommended."],
        ],
    },
    {
        "slug": "dmarc-record-syntax",
        "h1": "DMARC Record Syntax",
        "title": "DMARC Record Syntax: Every Tag Explained (v, p, rua, ruf, sp, pct, adkim, aspf)",
        "description": "DMARC record syntax: every tag explained. v, p, rua, ruf, sp, pct, adkim, aspf. Build correct v=DMARC1 records.",
        "entities": "DMARC record syntax, v=DMARC1, p=, rua=, ruf=, sp=, pct=, adkim=, aspf=, RFC 7489",
        "lead": "DMARC record syntax: every tag explained. v=DMARC1, p=, rua=, ruf=, sp=, pct=, adkim=, aspf=. RFC 7489.",
        "centerpiece_type": "table",
        "centerpiece": [
            ["Tag", "Required", "Values", "What it does"],
            ["v", "Yes", "DMARC1", "Protocol version (must be first tag)"],
            ["p", "Yes", "none / quarantine / reject", "Policy for the domain: what to do with failing mail"],
            ["rua", "No", "mailto:address", "Where to send aggregate reports (daily XML)"],
            ["ruf", "No", "mailto:address", "Where to send forensic reports (failure samples)"],
            ["sp", "No", "none / quarantine / reject", "Policy for subdomains (inherits p= if absent)"],
            ["pct", "No", "0-100 (default 100)", "Percentage of failing mail that receives the policy"],
            ["adkim", "No", "r (relaxed) / s (strict)", "DKIM alignment mode (default relaxed)"],
            ["aspf", "No", "r (relaxed) / s (strict)", "SPF alignment mode (default relaxed)"],
        ],
        "factual": [
            "A DMARC record is a DNS TXT record published at _dmarc.domain.com that starts with v=DMARC1 and defines the policy, reporting, and alignment settings for email authentication, as specified in RFC 7489.",
            "The p= tag is the only mandatory policy tag (after v=) and tells receiving servers what to do with mail that fails both SPF and DKIM alignment: none (deliver anyway), quarantine (send to spam), or reject (bounce).",
            "The rua= tag specifies the email address where mailbox providers send daily aggregate reports containing every source IP, message volume, and SPF/DKIM evaluation result for the domain.",
        ],
        "field_note": "The most common DMARC syntax error I see: using a semicolon after the last tag (causing a parsing warning), or forgetting that rua= requires the mailto: prefix. Always end the record without a trailing semicolon and always include mailto: before the reporting address.",
        "faqs": [
            ["Is the order of DMARC tags important?",
             "Only v=DMARC1 must be first. The other tags can appear in any order, separated by semicolons."],
            ["What happens if I omit the p= tag?",
             "The record is invalid and receivers ignore DMARC entirely. p= is mandatory."],
            ["Can I use a URL instead of mailto: for rua=?",
             "Yes, but mailto: is the most widely supported. HTTPS URIs (https://) are also allowed by RFC 7489 but less commonly implemented by mailbox providers."],
        ],
    },
    {
        "slug": "dmarc-policies",
        "h1": "DMARC Policies",
        "title": "DMARC Policies: p=none vs p=quarantine vs p=reject Explained",
        "description": "DMARC policies explained: p=none (monitor), p=quarantine (spam), p=reject (bounce). When to advance each step.",
        "entities": "DMARC policies, p=none, p=quarantine, p=reject, enforcement, pct=, aggregate reports, monitoring",
        "lead": "DMARC policies explained: p=none (monitor), p=quarantine (spam), p=reject (bounce). When to advance each.",
        "centerpiece_type": "comparison",
        "centerpiece": [
            ["Policy", "What happens to failing mail", "Score impact", "Risk"],
            ["p=none", "Delivered normally (monitor only)", "10/25", "Spoofed mail still delivered"],
            ["p=quarantine", "Delivered to spam folder", "20/25", "Legitimate mail may go to spam if not passing"],
            ["p=reject", "Bounced (not delivered)", "25/25", "Legitimate mail bounced if not passing"],
        ],
        "factual": [
            "DMARC policies define what receiving mail servers should do with messages that fail SPF and DKIM alignment: p=none delivers normally (monitoring only), p=quarantine delivers to the spam folder, and p=reject bounces the message.",
            "The pct= tag controls what percentage of failing mail receives the policy, enabling gradual rollout (e.g., pct=25 means only 25% of failing messages are quarantined while the rest are delivered).",
            "Advancing from p=none to p=quarantine to p=reject should only happen after aggregate reports confirm that every legitimate sending source passes SPF or DKIM alignment, to avoid bouncing your own email.",
        ],
        "field_note": "The fastest safe path to p=reject: start at p=none with rua= reporting, run for 2 weeks to identify all sources, fix any legitimate senders that fail, then jump directly to p=reject with pct=100. Skipping quarantine is safe if your aggregate reports show 100% pass rate for all known sources.",
        "faqs": [
            ["Can I go directly from p=none to p=reject?",
             "Yes, if your aggregate reports show 100% pass rate for all legitimate sources. The quarantine step is a safety net, not a requirement."],
            ["What does pct= do in practice?",
             "pct=25 with p=quarantine means only 25% of failing messages are quarantined; the other 75% are delivered normally. Increase gradually as confidence grows."],
        ],
    },
    {
        "slug": "dmarc-aggregate-reports",
        "h1": "DMARC Aggregate Reports",
        "title": "DMARC Aggregate Reports: How to Read RUA XML Reports from Gmail and Microsoft",
        "description": "DMARC aggregate reports: how to read RUA XML reports from Gmail, Microsoft. Source IPs, pass rates, dispositions.",
        "entities": "DMARC aggregate reports, RUA, XML, Gmail, Microsoft, source IP, pass rate, disposition, policy_evaluated",
        "lead": "DMARC aggregate reports: how to read RUA XML reports from Gmail and Microsoft. Source IPs, pass rates, dispositions.",
        "centerpiece_type": "table",
        "centerpiece": [
            ["Field in XML", "What it tells you"],
            ["report_metadata.org_name", "Who sent the report (google.com, microsoft.com, yahoo.com)"],
            ["report_metadata.date_range", "The 24-hour reporting window"],
            ["policy_published.domain", "Your domain (confirms the report is about you)"],
            ["record.row.source_ip", "The IP address that sent email claiming to be your domain"],
            ["record.row.count", "How many messages came from this IP in this period"],
            ["record.row.policy_evaluated.disposition", "What the receiver did: none, quarantine, or reject"],
            ["record.row.policy_evaluated.spf/dkim", "Whether SPF and DKIM passed alignment for this source"],
            ["record.identifiers.header_from", "The From header domain claimed by the sender"],
        ],
        "factual": [
            "A DMARC aggregate report is a daily XML document sent by mailbox providers to the rua= address in your DMARC record, containing a summary of all messages that claimed to be from your domain during a 24-hour period.",
            "Each record element in the XML represents a unique source IP address and includes the message count, SPF result, DKIM result, and the disposition (none, quarantine, or reject) applied by the receiving server.",
            "Aggregate reports do not contain message content: they are statistical summaries designed to help domain owners identify all legitimate sending sources and detect spoofing attempts.",
        ],
        "field_note": "The fastest way to identify a spoofing attempt: look for source IPs with high volume, failing DMARC, and a header_from that matches your domain. These are imposters. Legitimate sources you recognize should show pass rates above 90%.",
        "faqs": [
            ["Why do I receive multiple reports per day?",
             "Each mailbox provider (Gmail, Microsoft, Yahoo) sends its own report. If mail claiming to be from your domain passed through multiple providers, you receive one report from each."],
            ["What should I do with unknown source IPs?",
             "Check if the IP belongs to a service you use. If not, it may be a spoofing attempt. If your policy is p=none, the mail was delivered but flagged in the report."],
        ],
    },
    {
        "slug": "dmarc-forensic-reports",
        "h1": "DMARC Forensic Reports",
        "title": "DMARC Forensic Reports (RUF): Failure Samples with Full Message Content Explained",
        "description": "DMARC forensic reports (RUF): failure samples with full message content. Why most providers do not send them.",
        "entities": "DMARC forensic reports, RUF, failure samples, message content, privacy, RFC 6591, GDPR",
        "lead": "DMARC forensic reports (RUF): failure samples with full message content. Why most providers do not send them.",
        "centerpiece_type": "table",
        "centerpiece": [
            ["", "Aggregate (rua)", "Forensic (ruf)"],
            ["Content", "Statistical summary (counts, IPs, results)", "Full message sample including body and headers"],
            ["Privacy", "No message content, safe for GDPR", "Contains user email content, privacy concerns"],
            ["Frequency", "Daily", "Real-time (per failure)"],
            ["Provider support", "Gmail, Microsoft, Yahoo all send", "Almost none send (privacy regulations)"],
            ["Volume", "One report per provider per day", "One email per failure event"],
        ],
        "factual": [
            "A DMARC forensic report (ruf) is a real-time notification containing a sample of an individual message that failed DMARC evaluation, including the full message headers and often the body content.",
            "Almost no major mailbox provider sends forensic reports due to privacy concerns: forwarding the content of a user's email to a third party (the domain owner) may violate privacy regulations such as GDPR.",
            "The absence of forensic reports means domain owners must rely on aggregate reports (rua) for all DMARC monitoring, which provide statistical data but not individual message samples.",
        ],
        "field_note": "Do not configure ruf= expecting to receive failure samples: Gmail, Microsoft, and Yahoo do not send them. If you need message-level failure data, use a DMARC report processor that can parse aggregate reports and correlate source IPs with your known sending infrastructure.",
        "faqs": [
            ["Should I include ruf= in my DMARC record?",
             "You can include it, but do not expect reports from major providers. Some smaller providers or enterprise systems may send them."],
            ["Is there a privacy-safe alternative to ruf?",
             "Aggregate reports (rua) provide the same source IP and authentication data without exposing message content. This is the privacy-safe standard."],
        ],
    },
    {
        "slug": "how-to-create-dmarc-record",
        "h1": "How to Create a DMARC Record",
        "title": "How to Create a DMARC Record: Step-by-Step Guide with Correct Syntax",
        "description": "How to create a DMARC record: step by step with correct v=DMARC1 syntax for Cloudflare, Namecheap and GoDaddy.",
        "entities": "DMARC record, create, v=DMARC1, p=none, p=quarantine, p=reject, rua=, DNS TXT, _dmarc",
        "lead": "How to create a DMARC record: step by step with correct v=DMARC1 syntax for Cloudflare, Namecheap and GoDaddy.",
        "centerpiece_type": "steps",
        "centerpiece": [
            ["Step", "Action"],
            ["1", "Go to your DNS provider (Cloudflare, Namecheap, GoDaddy)"],
            ["2", "Add a TXT record with name: _dmarc.yourdomain.com (or _dmarc for root)"],
            ["3", "Set the value: v=DMARC1; p=none; rua=mailto:you@yourdomain.com"],
            ["4", "Wait 24-48 hours for aggregate reports to arrive"],
            ["5", "Read the reports, fix legitimate senders, then advance to quarantine and reject"],
        ],
        "factual": [
            "A DMARC record is created by adding a DNS TXT record at _dmarc.yourdomain.com that starts with v=DMARC1 and defines the policy and reporting configuration for email authentication.",
            "The p= tag controls what happens to mail that fails authentication: none (deliver normally, monitor only), quarantine (deliver to spam), or reject (bounce).",
            "The rua= tag specifies the email address where mailbox providers send daily aggregate reports, which are essential for identifying all legitimate sending sources before advancing the policy.",
        ],
        "field_note": "The mistake I see most often: publishing p=reject immediately without checking DMARC reports first. This bounces legitimate email from services you forgot about (billing systems, CRM tools, notification services). Always start at p=none and advance based on data.",
        "faqs": [
            ["How long does it take for a DMARC record to take effect?",
             "DNS propagation is fast (minutes on Cloudflare), but mailbox providers cache the policy. Changes typically take effect within 24-48 hours."],
            ["What if I already have a DMARC record?",
             "Edit the existing record to update the policy or add rua=. Do not create a second record: only one DMARC record per domain is valid."],
        ],
    },
    {
        "slug": "dmarc-enforcement-roadmap",
        "h1": "DMARC Enforcement Roadmap",
        "title": "DMARC Enforcement Roadmap: p=none to p=reject in 30-60 Days",
        "description": "DMARC enforcement roadmap: p=none to p=reject in 30-60 days. Step by step with aggregate report checkpoints.",
        "entities": "DMARC enforcement roadmap, p=none, p=quarantine, p=reject, pct=, aggregate reports, 30 days, 60 days",
        "lead": "DMARC enforcement roadmap: p=none to p=reject in 30-60 days with aggregate report checkpoints at each step.",
        "centerpiece_type": "steps",
        "centerpiece": [
            ["Phase", "Duration", "Action"],
            ["1: Monitor", "Days 1-14", "p=none with rua= reporting. Collect aggregate reports and identify all sources."],
            ["2: Fix", "Days 14-21", "Fix legitimate senders that fail DMARC (add include:, align return-path)."],
            ["3: Quarantine", "Days 21-35", "p=quarantine with pct=25, then pct=50, then pct=100."],
            ["4: Reject", "Days 35-60", "p=reject. All legitimate sources confirmed passing."],
        ],
        "factual": [
            "A DMARC enforcement roadmap is a structured plan for advancing from p=none (monitoring) to p=reject (full enforcement) using aggregate report data to confirm that every legitimate sending source passes authentication before the policy is tightened.",
            "The standard timeline is 30 to 60 days: two weeks at p=none to collect baseline data, one week to fix failing legitimate senders, two weeks at p=quarantine with pct= ramping from 25 to 100, then p=reject.",
            "Advancing DMARC policy without checking aggregate reports first risks bouncing legitimate email from forgotten services such as billing systems, CRM tools, or notification platforms that send as your domain.",
        ],
        "field_note": "The step that saves the most headaches: before advancing to p=quarantine, search your aggregate reports for any source IP with more than 1% of your volume that is failing. These are almost always legitimate services someone set up without IT's knowledge.",
        "faqs": [
            ["What if I skip the quarantine phase?",
             "You can go directly from p=none to p=reject if your aggregate reports show 100% pass rate. Quarantine is a safety net, not a requirement."],
            ["How do I roll back if legitimate mail is rejected?",
             "Lower pct= or revert to p=none. The DMARC record change propagates within minutes on Cloudflare. Then fix the failing source and re-advance."],
        ],
    },
    {
        "slug": "dmarc-pct-tag",
        "h1": "DMARC pct Tag",
        "title": "DMARC pct Tag: Gradual Policy Rollout with Percentage-Based Enforcement",
        "description": "DMARC pct= tag explained: gradual policy rollout with percentage-based enforcement. pct=25, pct=50, pct=100.",
        "entities": "DMARC pct tag, gradual rollout, pct=25, pct=50, pct=100, policy enforcement, percentage",
        "lead": "DMARC pct= tag explained: gradual policy rollout with percentage-based enforcement. pct=25, 50, 100.",
        "centerpiece_type": "table",
        "centerpiece": [
            ["pct= value", "Effect with p=quarantine", "Effect with p=reject"],
            ["100 (default)", "All failing mail goes to spam", "All failing mail is bounced"],
            ["50", "50% of failing mail to spam, 50% delivered", "50% bounced, 50% delivered"],
            ["25", "25% to spam, 75% delivered", "25% bounced, 75% delivered"],
            ["0", "No policy applied (same as p=none)", "No policy applied (same as p=none)"],
        ],
        "factual": [
            "The DMARC pct= tag controls the percentage of failing messages that receive the policy specified by p=, enabling gradual rollout of enforcement without affecting all failing mail simultaneously.",
            "The default value is 100, meaning all failing messages receive the policy. Setting pct=25 means only 25% of failing messages are quarantined or rejected while the remaining 75% are delivered normally.",
            "The pct= tag only applies when p= is quarantine or reject; it has no effect when p=none because no policy action is taken on failing messages.",
        ],
        "field_note": "The pct= tag is your safety net during enforcement rollout. Start at pct=25, watch aggregate reports for a week, then increase to 50, 75, and finally 100. If legitimate mail starts failing, reduce pct= immediately instead of reverting p=.",
        "faqs": [
            ["Does pct= affect aggregate reports?",
             "No. Reports are generated for all messages regardless of pct=. The tag only controls the enforcement action."],
            ["Can I use pct= with p=none?",
             "There is no effect. p=none already delivers all mail regardless of pct=."],
        ],
    },
    {
        "slug": "dmarc-subdomain-policy",
        "h1": "DMARC Subdomain Policy",
        "title": "DMARC Subdomain Policy (sp=): How Subdomains Inherit or Override DMARC",
        "description": "DMARC subdomain policy (sp=): how subdomains inherit or override the root DMARC policy. RFC 7489.",
        "entities": "DMARC subdomain policy, sp=, subdomain inheritance, p=, RFC 7489, _dmarc.subdomain",
        "lead": "DMARC subdomain policy (sp=): how subdomains inherit or override the root DMARC policy. RFC 7489.",
        "centerpiece_type": "table",
        "centerpiece": [
            ["Scenario", "Policy applied to subdomain"],
            ["No sp= tag, root p=none", "Subdomain inherits p=none"],
            ["No sp= tag, root p=reject", "Subdomain inherits p=reject"],
            ["sp=quarantine, root p=reject", "Subdomain uses p=quarantine, root uses p=reject"],
            ["DMARC record at _dmarc.sub.domain.com", "Subdomain uses its own record (overrides inheritance)"],
        ],
        "factual": [
            "The DMARC subdomain policy tag (sp=) defines a separate policy for subdomains of the primary domain, overriding the p= policy inherited from the root DMARC record.",
            "Without an sp= tag, all subdomains inherit the p= policy from the root domain's DMARC record, which means setting p=reject at the root also rejects failing mail from every subdomain.",
            "A subdomain can have its own DMARC record published at _dmarc.subdomain.domain.com, which overrides the inherited policy from the root domain for that specific subdomain.",
        ],
        "field_note": "The sp= tag is essential when you have subdomains that send email with their own infrastructure. Without it, tightening p=reject at the root also enforces DMARC on every subdomain, potentially breaking legitimate email from development or staging environments.",
        "faqs": [
            ["Does DMARC automatically apply to all subdomains?",
             "Yes, unless an sp= tag overrides the policy or the subdomain has its own DMARC record at _dmarc.subdomain.domain.com."],
            ["Can I set p=none for a subdomain while the root is p=reject?",
             "Yes, by using sp=none in the root DMARC record, or by publishing a separate DMARC record at _dmarc.subdomain.domain.com with p=none."],
        ],
    },
    {
        "slug": "dmarc-vs-spf-vs-dkim",
        "h1": "DMARC vs SPF vs DKIM",
        "title": "DMARC vs SPF vs DKIM: How All Three Work Together for Email Authentication",
        "description": "DMARC vs SPF vs DKIM: how all three work together. SPF authorizes IPs, DKIM signs content, DMARC sets policy.",
        "entities": "DMARC, SPF, DKIM, RFC 7489, RFC 7208, RFC 6376, alignment, authentication, policy",
        "lead": "DMARC vs SPF vs DKIM: how all three work together. SPF authorizes IPs, DKIM signs content, DMARC sets policy.",
        "centerpiece_type": "comparison",
        "centerpiece": [
            ["", "SPF", "DKIM", "DMARC"],
            ["RFC", "7208", "6376", "7489"],
            ["What it does", "Authorizes sending IPs", "Signs message content", "Sets policy + reports"],
            ["DNS record", "TXT at root (v=spf1)", "TXT at selector._domainkey", "TXT at _dmarc"],
            ["Survives forwarding", "No", "Yes", "Depends on which protocol aligns"],
            ["Provides reports", "No", "No", "Yes (aggregate via rua=)"],
            ["Stops spoofing alone?", "Partially (IP-based)", "Partially (crypto-based)", "Yes (enforcement layer)"],
            ["Works without the others?", "Yes (but weak alone)", "Yes (but weak alone)", "No (needs SPF or DKIM)"],
        ],
        "factual": [
            "SPF, DKIM, and DMARC are three complementary email authentication protocols that work together: SPF (RFC 7208) authorizes sending IP addresses, DKIM (RFC 6376) cryptographically signs message content, and DMARC (RFC 7489) defines the enforcement policy and reporting mechanism.",
            "DMARC requires at least one of SPF or DKIM to pass AND align with the visible From header domain; using both provides redundancy because SPF fails on forwarding while DKIM survives it.",
            "SPF and DKIM without DMARC provide authentication signals but no enforcement: receiving servers have no policy telling them what to do with messages that fail authentication.",
        ],
        "field_note": "The most resilient email authentication setup I have implemented uses all three: SPF as the baseline, DKIM as the forward-safe layer, and DMARC as the enforcement and reporting layer. Any two passing is sufficient for DMARC alignment, but all three passing is the goal.",
        "faqs": [
            ["Which of the three is most important?",
             "DMARC, because it provides enforcement and reporting. But DMARC requires SPF or DKIM to pass first, so all three are needed for a complete setup."],
            ["Do I need all three for email deliverability?",
             "Gmail and Microsoft recommend all three for bulk senders. Two (SPF + DKIM) provide redundancy; DMARC adds enforcement."],
        ],
    },
    {
        "slug": "bimi-record",
        "h1": "BIMI Record",
        "title": "BIMI Record: Display Your Brand Logo in Email Inboxes (DMARC Required)",
        "description": "BIMI record: display your brand logo in Gmail and Apple Mail. Requires DMARC enforcement and a VMC certificate.",
        "entities": "BIMI record, brand logo, Gmail, Apple Mail, VMC, VMC certificate, DMARC enforcement, SVG",
        "lead": "BIMI record: display your brand logo in Gmail and Apple Mail inboxes. Requires DMARC enforcement and VMC.",
        "centerpiece_type": "table",
        "centerpiece": [
            ["Requirement", "Details"],
            ["DMARC enforcement", "p=quarantine or p=reject (p=none is not sufficient)"],
            ["DNS record", "TXT at default._bimi.domain.com: v=BIMI1; l=https://url/to/logo.svg"],
            ["Logo format", "SVG Tiny 1.2 profile (specific requirements apply)"],
            ["VMC certificate", "Verified Mark Certificate from DigiCert or Entrust (required for Gmail)"],
            ["Supported providers", "Gmail, Apple Mail (iOS 16+), Yahoo Mail, Fastmail"],
        ],
        "factual": [
            "A BIMI (Brand Indicators for Message Identification) record is a DNS TXT record published at default._bimi.domain.com that specifies the location of a brand logo to be displayed next to verified email messages in supporting inbox providers.",
            "BIMI requires DMARC enforcement at p=quarantine or p=reject as a prerequisite, ensuring that only authenticated email from the domain displays the brand logo.",
            "Gmail additionally requires a Verified Mark Certificate (VMC) issued by a trusted certificate authority to validate the trademark ownership of the logo before displaying it.",
        ],
        "field_note": "BIMI is a post-DMARC feature: do not attempt it until DMARC enforcement is at p=quarantine or p=reject. The VMC certificate costs $1,000-1,500 per year, which is a significant investment for the logo display benefit.",
        "faqs": [
            ["Is BIMI free?",
             "The DNS record is free, but Gmail requires a VMC certificate ($1,000-1,500/year) to display the logo. Apple Mail may work without a VMC in some cases."],
            ["What logo format does BIMI require?",
             "SVG Tiny 1.2 (a specific SVG profile). The logo must be square, fit within specific dimensions, and have no external references."],
        ],
    },
    {
        "slug": "bimi-vmc",
        "h1": "BIMI VMC Certificate",
        "title": "BIMI VMC Certificate: Verified Mark Certificate Requirements and Providers",
        "description": "BIMI VMC certificate: Verified Mark Certificate requirements, providers (DigiCert, Entrust) and pricing.",
        "entities": "BIMI VMC, Verified Mark Certificate, DigiCert, Entrust, pricing, trademark, Gmail BIMI",
        "lead": "BIMI VMC certificate: Verified Mark Certificate requirements, providers and pricing for Gmail BIMI.",
        "centerpiece_type": "table",
        "centerpiece": [
            ["Provider", "VMC Price (approx.)", "CMC Available"],
            ["DigiCert", "$1,000-1,500/year", "No"],
            ["Entrust", "$1,000-1,500/year", "Yes (for some providers)"],
            ["MarkValidator (via SSL.com)", "Varies", "Yes"],
        ],
        "factual": [
            "A Verified Mark Certificate (VMC) is a digital certificate issued by a trusted certificate authority that validates the trademark ownership of a brand's logo for BIMI display in email inboxes.",
            "Gmail requires a VMC for BIMI logo display, while Apple Mail may accept a Common Mark Certificate (CMC) which has less stringent trademark verification requirements.",
            "The VMC issuance process requires a registered trademark for the logo, verification of the organization's legal identity, and a validation process similar to Extended Validation (EV) certificates.",
        ],
        "field_note": "The VMC is the most expensive part of BIMI deployment. For small organizations, the cost may not be justified until email volume and brand recognition make the logo display benefit worthwhile.",
        "faqs": [
            ["Do I need a trademark to get a VMC?",
             "Yes. The logo must be a registered trademark with a government trademark office. This is verified during the VMC issuance process."],
            ["Is a CMC cheaper than a VMC?",
             "Yes. Common Mark Certificates have less stringent verification requirements and may be available for some providers without a full trademark registration."],
        ],
    },
    {
        "slug": "mta-sts-record",
        "h1": "MTA-STS Record",
        "title": "MTA-STS Record: Enforce TLS for Email Delivery via DNS and HTTPS Policy",
        "description": "MTA-STS record: enforce TLS for email delivery via DNS TXT record and HTTPS-hosted policy file. RFC 8460.",
        "entities": "MTA-STS record, SMTP TLS enforcement, RFC 8460, DNS TXT, HTTPS policy, _smtp._tls",
        "lead": "MTA-STS record: enforce TLS for email delivery via DNS TXT and HTTPS policy file. RFC 8460.",
        "centerpiece_type": "table",
        "centerpiece": [
            ["Component", "Location", "Purpose"],
            ["DNS TXT record", "_smtp._tls.domain.com", "Signals MTA-STS support: v=STS1"],
            ["HTTPS policy file", "https://mta-sts.domain.com/.well-known/mta-sts.txt", "Defines TLS policy: mode, max_age, MX hosts"],
            ["DNS TXT record (TLS-RPT)", "_smtp._tls.domain.com (separate record)", "Reporting address for TLS failures: v=TLSRPTv1; rua=..."],
        ],
        "factual": [
            "An MTA-STS (SMTP Mail Transfer Agent Strict Transport Security) record is a DNS TXT record published at _smtp._tls.domain.com that signals a domain's support for TLS-enforced email delivery, as defined in RFC 8460.",
            "The MTA-STS policy file is hosted at https://mta-sts.domain.com/.well-known/mta-sts.txt and defines the enforcement mode (none, testing, or enforce), the maximum policy age, and the list of expected MX hosts.",
            "MTA-STS prevents downgrade attacks where an attacker strips the STARTTLS encryption from SMTP connections, forcing email to be transmitted in plaintext.",
        ],
        "field_note": "MTA-STS is the easiest TLS enforcement mechanism to deploy (compared to DANE) because it uses HTTPS rather than DNSSEC. The policy file must be served over HTTPS with a valid certificate for mta-sts.domain.com.",
        "faqs": [
            ["What is the difference between testing and enforce mode?",
             "Testing mode reports TLS failures without affecting delivery. Enforce mode requires valid TLS and bounces connections that do not support it."],
            ["Does Cloudflare Email Routing support MTA-STS?",
             "Yes, Cloudflare Email Routing supports STARTTLS. Publishing an MTA-STS policy in enforce mode requires that all MX hosts support TLS."],
        ],
    },
    {
        "slug": "tls-rpt",
        "h1": "TLS-RPT",
        "title": "TLS-RPT: SMTP TLS Reporting for Email Delivery Failure Diagnostics (RFC 8460)",
        "description": "TLS-RPT explained: SMTP TLS reporting via DNS TXT record. Daily JSON reports of TLS connection failures. RFC 8460.",
        "entities": "TLS-RPT, SMTP TLS reporting, RFC 8460, DNS TXT record, _smtp._tls, JSON reports, TLS failures",
        "lead": "TLS-RPT explained: SMTP TLS reporting via DNS TXT record. Daily JSON reports of TLS failures. RFC 8460.",
        "centerpiece_type": "table",
        "centerpiece": [
            ["Field", "Details"],
            ["DNS record location", "_smtp._tls.domain.com TXT"],
            ["Record value", "v=TLSRPTv1; rua=mailto:tls-reports@domain.com"],
            ["Report format", "JSON (daily summary of TLS connection results)"],
            ["Report senders", "Gmail, Microsoft, and other supporting providers"],
            ["Companion protocol", "MTA-STS (RFC 8460) for TLS enforcement"],
        ],
        "factual": [
            "TLS-RPT (SMTP TLS Reporting) is a mechanism defined in RFC 8460 that allows receiving mail servers to send daily JSON reports to the sending domain about TLS connection success and failure rates.",
            "The DNS TXT record at _smtp._tls.domain.com contains the reporting address (rua=) where providers deliver these daily JSON summary reports.",
            "TLS-RPT is designed to work alongside MTA-STS (RFC 8460) to provide visibility into TLS deployment issues: MTA-STS enforces TLS while TLS-RPT reports on what happened.",
        ],
        "field_note": "TLS-RPT costs nothing to deploy (one DNS record) and provides invaluable visibility into whether your email is actually being transmitted over TLS. It is a prerequisite for MTA-STS deployment.",
        "faqs": [
            ["Do I need MTA-STS to use TLS-RPT?",
             "No. TLS-RPT works independently and reports TLS connection outcomes whether or not MTA-STS is deployed."],
            ["What do the TLS-RPT JSON reports contain?",
             "Daily summaries: total successful TLS connections, total failures, and failure details (certificate errors, handshake failures, etc.)."],
        ],
    },
    {
        "slug": "tls-rpt-record",
        "h1": "TLS-RPT Record",
        "title": "TLS-RPT Record: How to Create the _smtp._tls DNS TXT Record for TLS Reporting",
        "description": "TLS-RPT record: how to create the _smtp._tls DNS TXT record for SMTP TLS reporting. RFC 8460 syntax.",
        "entities": "TLS-RPT record, _smtp._tls, DNS TXT, v=TLSRPTv1, rua=, RFC 8460, create",
        "lead": "TLS-RPT record: how to create the _smtp._tls DNS TXT record for SMTP TLS reporting.",
        "centerpiece_type": "steps",
        "centerpiece": [
            ["Step", "Action"],
            ["1", "Go to your DNS provider (Cloudflare, Namecheap, GoDaddy)"],
            ["2", "Add a TXT record with name: _smtp._tls.yourdomain.com"],
            ["3", "Set the value: v=TLSRPTv1; rua=mailto:tls-reports@yourdomain.com"],
            ["4", "Save and verify with our free tools"],
        ],
        "factual": [
            "A TLS-RPT record is a DNS TXT record published at _smtp._tls.domain.com that contains a v=TLSRPTv1 declaration and a rua= reporting address where mailbox providers deliver daily JSON reports about TLS connection outcomes.",
            "The record follows the syntax defined in RFC 8460 and must be published as a single TXT record at the exact name _smtp._tls.domain.com (not at the root or at a subdomain other than _smtp._tls).",
            "TLS-RPT is most useful when combined with MTA-STS: TLS-RPT provides the visibility into TLS failures while MTA-STS provides the enforcement mechanism.",
        ],
        "field_note": "TLS-RPT requires zero maintenance after deployment: the DNS record never changes, and the reports arrive automatically. It is the lowest-effort, highest-visibility DNS security improvement.",
        "faqs": [
            ["Can I use the same reporting address for TLS-RPT and DMARC rua=?",
             "Yes, the same mailbox can receive both TLS-RPT and DMARC reports. They are different formats and can be distinguished by content."],
            ["Does TLS-RPT require DNSSEC?",
             "No. TLS-RPT is a plain DNS TXT record and does not require DNSSEC validation."],
        ],
    },
    {
        "slug": "arc-seal-explained",
        "h1": "ARC Seal Explained",
        "title": "ARC Seal Explained: How Authenticated Received Chain Preserves Email Authentication on Forwarding",
        "description": "ARC seal explained: how Authenticated Received Chain preserves SPF and DKIM results when email is forwarded. RFC 8617.",
        "entities": "ARC seal, Authenticated Received Chain, RFC 8617, forwarding, SPF, DKIM, mailing list, intermediate server",
        "lead": "ARC seal explained: how Authenticated Received Chain preserves SPF and DKIM results when email is forwarded. RFC 8617.",
        "centerpiece_type": "table",
        "centerpiece": [
            ["Scenario", "Without ARC", "With ARC"],
            ["Direct delivery", "SPF + DKIM pass normally", "Same"],
            ["Forwarded via mailing list", "SPF fails (new IP), DKIM may break (body modified)", "ARC seal preserves the original authentication results"],
            ["Forwarded via auto-forwarder", "SPF fails (new IP)", "ARC seal maintains the authentication chain"],
            ["Gmail treatment", "May show as unauthenticated", "Accepts ARC-sealed original results"],
        ],
        "factual": [
            "ARC (Authenticated Received Chain) is an email authentication protocol defined in RFC 8617 that preserves the original SPF and DKIM authentication results when a message passes through intermediate servers (such as mailing lists or forwarding services) that modify the message.",
            "Each intermediate server that handles the message adds an ARC-Authentication-Results header and an ARC-Message-Signature header, creating a chain of custody that the final receiver can evaluate.",
            "ARC addresses the fundamental limitation of SPF and DKIM: both break when an intermediate server modifies the message or sends from a different IP, which is common with mailing lists and forwarding services.",
        ],
        "field_note": "ARC adoption is growing but not universal: Gmail and Microsoft support it, but many smaller providers do not evaluate ARC chains yet. If your emails fail SPF after forwarding, ARC is the emerging solution but traditional fixes (subdomain separation, SRS) are still more widely effective.",
        "faqs": [
            ["Does ARC replace SPF and DKIM?",
             "No. ARC preserves the original SPF and DKIM results through intermediary servers. The underlying authentication must still pass at the first hop."],
            ["Do I need to deploy ARC on my mail server?",
             "Only if your server is an intermediate hop (mailing list, forwarder). End-user mail servers do not need ARC; they evaluate it if present."],
        ],
    },
    {
        "slug": "spf-vs-dmarc",
        "h1": "SPF vs DMARC",
        "title": "SPF vs DMARC: What Each Protocol Does and Why DMARC Requires SPF",
        "description": "SPF vs DMARC: SPF authorizes IPs, DMARC sets policy and reports. DMARC requires SPF or DKIM to pass first.",
        "entities": "SPF, DMARC, RFC 7208, RFC 7489, alignment, policy, aggregate reports, IP authorization",
        "lead": "SPF vs DMARC: SPF authorizes IPs, DMARC sets policy and reports. DMARC requires SPF or DKIM to pass.",
        "centerpiece_type": "comparison",
        "centerpiece": [
            ["", "SPF", "DMARC"],
            ["RFC", "7208", "7489"],
            ["What it does", "Authorizes sending IP addresses", "Defines enforcement policy and reporting"],
            ["DNS record", "TXT at root: v=spf1 ...", "TXT at _dmarc: v=DMARC1; p=..."],
            ["Stops spoofing?", "Only for IPs not in the record", "Yes (enforces SPF/DKIM results)"],
            ["Provides reports?", "No", "Yes (rua= aggregate reports)"],
            ["Requires other protocols?", "No", "Yes (needs SPF or DKIM to pass)"],
        ],
        "factual": [
            "SPF and DMARC are sequential email authentication protocols: SPF (RFC 7208) authorizes sending IP addresses via a DNS TXT record, while DMARC (RFC 7489) builds on those results to enforce a policy and generate reports.",
            "DMARC cannot function without SPF or DKIM: it requires at least one of those protocols to pass and align with the From header domain before it can apply its policy.",
            "SPF alone provides IP authorization but no enforcement or reporting: DMARC adds the policy layer (p=none, quarantine, reject) and the aggregate reporting mechanism (rua=).",
        ],
        "field_note": "The progression I always recommend: SPF first (authorize your IPs), then DKIM (forward-safe authentication), then DMARC (enforcement + visibility). Each layer builds on the previous one.",
        "faqs": [
            ["Can I use DMARC without SPF?",
             "Yes, if DKIM passes and aligns. But using both SPF and DKIM provides better coverage."],
            ["Does SPF stop email spoofing?",
             "Partially. SPF prevents IP spoofing but not header spoofing. DMARC closes that gap by requiring alignment with the From header."],
        ],
    },
]

# Generate each page
count = 0
for pg in PAGES:
    slug = pg["slug"]
    out = TPL_DIR / f"{slug}.astro"

    is_comparison = pg["centerpiece_type"] == "comparison"
    is_steps = pg["centerpiece_type"] == "steps"

    # Build centerpiece HTML manually (Astro can't use Python f-string logic)
    headers = pg["centerpiece"][0]
    rows = pg["centerpiece"][1:]

    th = "".join(f"<th class='whitespace-nowrap'>{h}</th>" for h in headers)
    trs = ""
    for row in rows:
        tds = ""
        for ci, v in enumerate(row):
            cls = " class='pd-mono'" if ci == 0 or headers[ci] in ("Type", "Tag", "pct= value", "Step", "Mechanism") else ""
            tds += f"<td{cls}>{v}</td>"
        trs += f"<tr>{tds}</tr>"
    table_html = f"<table class='pdns-table' style='width:100%'><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table>"

    factual_ps = "".join(f"<p class='mt-3'>{p}</p>" for p in pg["factual"])

    faq_items = ""
    for q, a in pg["faqs"]:
        faq_items += (
            f'<details class="group rounded-xl border border-line bg-panel/60 px-5 py-4 open:border-accent/40">'
            f'<summary class="flex cursor-pointer list-none items-center justify-between gap-4 font-semibold text-ink [&::-webkit-details-marker]:hidden">{q}'
            '<span class="text-accent transition-transform duration-200 group-open:rotate-45">+</span></summary>'
            f'<p class="mt-3 text-sm leading-relaxed text-ink-dim">{a}</p></details>'
        )

    faqs_json = json.dumps(pg["faqs"], ensure_ascii=False)
    h1_json = json.dumps(pg["h1"], ensure_ascii=False)
    desc_json = json.dumps(pg["description"], ensure_ascii=False)

    page_content = f"""---
import BaseLayout from '../layouts/BaseLayout.astro';

const faqs = {faqs_json};

const article = {{
  '@context': 'https://schema.org',
  '@type': 'Article',
  headline: {h1_json},
  description: {desc_json},
  inLanguage: 'en',
  author: {{ '@type': 'Organization', name: 'PromptDNS', url: 'https://promptdns.com/' }},
  publisher: {{ '@type': 'Organization', name: 'PromptDNS', url: 'https://promptdns.com/', logo: {{ '@type': 'ImageObject', url: 'https://promptdns.com/favicon.svg' }} }},
  datePublished: '{DATE_PUBLISHED}',
  dateModified: '{DATE_PUBLISHED}',
}};

const faqSchema = {{
  '@context': 'https://schema.org',
  '@type': 'FAQPage',
  mainEntity: faqs.map(([q, a]) => ({{
    '@type': 'Question',
    name: q,
    acceptedAnswer: {{ '@type': 'Answer', text: a }},
  }})),
}};

const breadcrumbs = {{
  '@context': 'https://schema.org',
  '@type': 'BreadcrumbList',
  itemListElement: [
    {{ '@type': 'ListItem', position: 1, name: 'Home', item: 'https://promptdns.com/' }},
    {{ '@type': 'ListItem', position: 2, name: 'Email Authentication', item: 'https://promptdns.com/email-authentication/' }},
    {{ '@type': 'ListItem', position: 3, name: {h1_json} }},
  ],
}};
---
<BaseLayout
  title="{pg['title']}"
  description="{pg['description']}"
  schema={{[article, faqSchema, breadcrumbs]}}
>
  <div class="mx-auto max-w-4xl px-4 py-12">
    <nav class="mb-4 text-sm text-ink-faint" aria-label="Breadcrumb">
      <a href="/" class="hover:text-accent">Home</a>
      <span aria-hidden="true">/</span>
      <a href="/email-authentication/" class="hover:text-accent">Email Authentication</a>
      <span aria-hidden="true">/</span>
      <span class="text-ink-dim">{pg['h1']}</span>
    </nav>
    <h1 class="font-display text-3xl font-bold tracking-tight text-ink sm:text-4xl">{pg['h1']}</h1>
    <p class="mt-4 text-lg text-ink-dim">{pg['lead']}</p>

    <section class="not-prose my-8" aria-label="Reference table">
      <div class="glass rounded-2xl p-5 shadow-lg sm:p-7 overflow-x-auto">
        {table_html}
      </div>
    </section>

    <article class="rich-text mt-10 max-w-none">
      <h2>Technical details</h2>
      {factual_ps}

      <aside class="mt-8 rounded-xl border-l-3 border-l-violet/50 bg-violet/5 p-5" aria-label="Practitioner field notes">
        <p class="font-mono text-[10px] uppercase tracking-[0.16em] text-violet mb-2">Field notes</p>
        <p class="text-sm leading-relaxed text-ink-dim italic">{pg['field_note']}</p>
      </aside>

      <h2 class="font-display mt-10 text-xl font-semibold text-ink">Frequently asked questions</h2>
      <div class="mt-3 grid gap-3">
        {faq_items}
      </div>

      <p class="mt-8 text-xs text-ink-faint">
        Check your domain with our free tools:
        <a href="/spf-record-checker/" class="text-accent hover:text-accent-soft">SPF checker</a>,
        <a href="/dmarc-record-checker/" class="text-accent hover:text-accent-soft">DMARC checker</a>,
        <a href="/dkim-record-checker/" class="text-accent hover:text-accent-soft">DKIM checker</a>.
      </p>
    </article>
  </div>
</BaseLayout>
"""

    out.write_text(page_content, encoding="utf-8")
    count += 1
    print(f"Generated: {slug}")

print(f"\n{count} pages generated")
