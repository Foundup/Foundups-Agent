/**
 * @packageDocumentation
 *
 * ```typescript
 * import { uriToMultiaddr } from '@multiformats/uri-to-multiaddr'
 *
 * console.log(uriToMultiaddr('https://protocol.ai'))
 * // -> /dns4/protocol.ai/tcp/443/https
 * ```
 *
 * Domain names can represent one of
 *
 * - `/dns4` - domain resolves to an ipv4 address (**default**)
 * - `/dns6` - domain resolves to an ipv6 address
 * - `/dnsaddr` - domain has a [DNSLink](https://docs.ipfs.io/guides/concepts/dnslink/) TXT record pointing to an IPFS CID
 *
 * This library assumes `/dns4` when it finds a domain name in the input string.
 * It makes no attempt query DNS. To override the default assumption, you can pass
 * in an options object as the second parameter to override it:
 *
 * ```typescript
 * import { uriToMultiaddr } from '@multiformats/uri-to-multiaddr'
 *
 * console.log(uriToMultiaddr('https://protocol.ai'), { defaultDnsType: 'dns6' })
 * // -> /dns6/protocol.ai/tcp/443/https
 * ```
 *
 * See [test.js](./test.js) for the currently supported conversions.
 *
 * **Note**: `uri-to-multiaddr` will throw if the passed URI:
 *
 * - is not a valid, according the WHATWG URL spec implementation used.
 * - is not supported yet
 *
 * ## Related
 *
 * - [@multiformats/multiaddr-to-uri](https://github.com/multiformats/js-multiaddr-to-uri) - convert it back again
 */

import { multiaddr } from '@multiformats/multiaddr'
import { isIPv4, isIPv6 } from 'is-ip'
import type { Multiaddr } from '@multiformats/multiaddr'

const portFor: Record<string, string> = {
  http: '80',
  https: '443',
  ws: '80',
  wss: '443'
}

const BROWSER_SCHEMES = ['http', 'https', 'ws', 'wss']

export interface MultiaddrFromUriOpts {
  /**
   * If a URI contains a domain name, by default the `/dns/` tuple will be used
   * to define it. If you wish to use `/dnsaddr` or something more specific like
   * `/dns4` or `/dns6`, pass it as an option here.
   *
   * @default 'dns'
   */
  defaultDnsType?: 'dns' | 'dns4' | 'dns6' | 'dnsaddr'
}

/**
 * Convert a URI to a multiaddr
 *
 * http://foobar.com => /dns/foobar.com/tcp/80/http
 * https://foobar.com => /dns/foobar.com/tcp/443/https
 * https://foobar.com:5001 => /dns/foobar.com/tcp/5001/https
 * https://127.0.0.1:8080 => /ip4/127.0.0.1/tcp/8080/https
 * http://[::1]:8080 => /ip6/::1/tcp/8080/http
 * tcp://foobar.com:8080 => /dns/foobar.com/tcp/8080
 * udp://foobar.com:8080 => /dns/foobar.com/udp/8080
 */

export function uriToMultiaddr (uriStr: string, opts?: MultiaddrFromUriOpts): Multiaddr {
  opts = opts ?? {}
  const defaultDnsType = opts.defaultDnsType ?? 'dns'
  const { scheme, hostname, port, path } = parseUri(uriStr)
  const parts = [
    tupleForHostname(hostname, defaultDnsType),
    tupleForPort(port, scheme),
    tupleForScheme(scheme)
  ]

  if (path != null) {
    parts.push(tupleForPath(path))
  }

  const multiaddrStr = '/' + parts
    .filter(x => Boolean(x))
    // @ts-expect-error ts cannot see we filter falsy values
    .reduce((a, b) => a.concat(b), [])
    .join('/')

  return multiaddr(multiaddrStr)
}

function parseUri (uriStr: string): { scheme: string, hostname: string, port: string, path?: string } {
  const [scheme] = uriStr.split(':')

  // browsers will only parse URLs with schemes they understand
  if (!BROWSER_SCHEMES.includes(scheme)) {
    uriStr = 'http' + uriStr.substring(scheme.length)
  }

  // Use the WHATWG URL global, in node >= 10 and the browser
  let { protocol, hostname, port, pathname, search } = new URL(uriStr)

  if (port == null || port === '') {
    const protocolPort = portForProtocol(scheme)

    if (protocolPort != null) {
      port = protocolPort
    }

    // browsers will omit the port when it's common
    if (protocolPort == null && protocol === 'http:') {
      // we overrode the protocol with http, set the port to 80
      port = '80'
    }
  }

  let path: string | undefined

  if (pathname != null && pathname !== '' && pathname !== '/') {
    if (pathname.startsWith('/')) {
      pathname = pathname.substring(1)
    }

    path = pathname
  }

  if (search != null && search !== '') {
    path = path ?? ''
    path += search
  }

  return { scheme, hostname, port, path }
}

function tupleForHostname (hostname: string, defaultDnsType: string): [string, string] | undefined {
  if (hostname == null || hostname === '') {
    return undefined
  }

  if (isIPv4(hostname)) {
    return ['ip4', hostname]
  }

  if (isIPv6(hostname)) {
    return ['ip6', hostname]
  }

  // literal ipv6 in url should be wrapped in square brackets [x:y:z]
  // https://www.ietf.org/rfc/rfc2732.txt
  if (hostname[0] === '[') {
    const trimmed = hostname.substring(1, hostname.length - 1)
    if (isIPv6(trimmed)) {
      return ['ip6', trimmed]
    }
  }
  // assumes that any non-ip hostname is a dns4 address.
  return [defaultDnsType, hostname]
}

function tupleForPort (port: string, scheme: string): [string, string] | undefined {
  if (port == null || port === '') {
    return undefined
  }

  if (scheme === 'udp') {
    return ['udp', port]
  }

  return ['tcp', port]
}

function tupleForScheme (scheme: string): [string] | undefined {
  if (scheme.match(/^tcp$|^udp$/) != null) {
    return undefined
  }

  if (scheme === 'https') {
    return ['/tls/http']
  }

  if (scheme === 'wss') {
    return ['/tls/ws']
  }

  return [scheme]
}

function tupleForPath (path: string): [string, string] | undefined {
  if (path == null || path === '') {
    return undefined
  }

  return ['http-path', encodeURIComponent(path)]
}

function portForProtocol (protocol: string): string | undefined {
  if (protocol == null || protocol === '' || portFor[protocol] == null) {
    return undefined
  }

  return portFor[protocol]
}
