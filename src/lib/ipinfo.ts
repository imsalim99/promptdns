/**
 * IP intelligence: public IP discovery, geolocation/ASN, reverse DNS (PTR via
 * our own DoH engine, the unique bit).
 */
import { lookup, RESOLVERS } from './doh';
import { reverseIp } from './dnsbl';

export interface IpInfo {
  ip: string;
  ptr: string | null;
  country?: string;
  city?: string;
  region?: string;
  lat?: number;
  lon?: number;
  asn?: string;
  org?: string;
  isp?: string;
  type?: string;
  via: string;
}

export async function getMyIp(): Promise<string> {
  const res = await fetch('https://api.ipify.org?format=json');
  if (!res.ok) throw new Error('Could not determine your IP.');
  const j = (await res.json()) as { ip: string };
  return j.ip;
}

export async function ptrOf(ip: string): Promise<string | null> {
  const res = await lookup(reverseIp(ip), 'PTR', RESOLVERS[0]);
  const ptr = res.answers.find((x) => x.type === 12)?.data;
  return ptr ? ptr.replace(/\.$/, '') : null;
}

export async function ipInfo(ip: string): Promise<IpInfo> {
  const [ptrRes, geoRes] = await Promise.allSettled([ptrOf(ip), fetch(`https://ipwho.is/${ip}`)]);
  const ptr = ptrRes.status === 'fulfilled' ? ptrRes.value : null;

  let geo: Record<string, unknown> | null = null;
  if (geoRes.status === 'fulfilled' && geoRes.value.ok) {
    try { geo = (await geoRes.value.json()) as Record<string, unknown>; } catch { geo = null; }
  }

  const connection = (geo?.connection ?? {}) as Record<string, unknown>;
  return {
    ip,
    ptr,
    country: geo?.country as string | undefined,
    city: geo?.city as string | undefined,
    region: geo?.region as string | undefined,
    lat: geo?.latitude as number | undefined,
    lon: geo?.longitude as number | undefined,
    asn: connection.asn ? `AS${connection.asn}` : undefined,
    org: connection.org as string | undefined,
    isp: connection.isp as string | undefined,
    type: geo?.type as string | undefined,
    via: geo ? 'ipwho.is + PromptDNS PTR' : 'PromptDNS PTR only',
  };
}
