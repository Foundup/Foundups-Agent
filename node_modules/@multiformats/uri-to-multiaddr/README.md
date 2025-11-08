# @multiformats/uri-to-multiaddr

[![multiformats.io](https://img.shields.io/badge/project-IPFS-blue.svg?style=flat-square)](http://multiformats.io)
[![codecov](https://img.shields.io/codecov/c/github/multiformats/js-uri-to-multiaddr.svg?style=flat-square)](https://codecov.io/gh/multiformats/js-uri-to-multiaddr)
[![CI](https://img.shields.io/github/actions/workflow/status/multiformats/js-uri-to-multiaddr/js-test-and-release.yml?branch=main\&style=flat-square)](https://github.com/multiformats/js-uri-to-multiaddr/actions/workflows/js-test-and-release.yml?query=branch%3Amain)

> Convert a URI to a Multiaddr

# About

<!--

!IMPORTANT!

Everything in this README between "# About" and "# Install" is automatically
generated and will be overwritten the next time the doc generator is run.

To make changes to this section, please update the @packageDocumentation section
of src/index.js or src/index.ts

To experiment with formatting, please run "npm run docs" from the root of this
repo and examine the changes made.

-->

```typescript
import { uriToMultiaddr } from '@multiformats/uri-to-multiaddr'

console.log(uriToMultiaddr('https://protocol.ai'))
// -> /dns4/protocol.ai/tcp/443/https
```

Domain names can represent one of

- `/dns4` - domain resolves to an ipv4 address (**default**)
- `/dns6` - domain resolves to an ipv6 address
- `/dnsaddr` - domain has a [DNSLink](https://docs.ipfs.io/guides/concepts/dnslink/) TXT record pointing to an IPFS CID

This library assumes `/dns4` when it finds a domain name in the input string.
It makes no attempt query DNS. To override the default assumption, you can pass
in an options object as the second parameter to override it:

```typescript
import { uriToMultiaddr } from '@multiformats/uri-to-multiaddr'

console.log(uriToMultiaddr('https://protocol.ai'), { defaultDnsType: 'dns6' })
// -> /dns6/protocol.ai/tcp/443/https
```

See [test.js](./test.js) for the currently supported conversions.

**Note**: `uri-to-multiaddr` will throw if the passed URI:

- is not a valid, according the WHATWG URL spec implementation used.
- is not supported yet

## Related

- [@multiformats/multiaddr-to-uri](https://github.com/multiformats/js-multiaddr-to-uri) - convert it back again

# Install

```console
$ npm i @multiformats/uri-to-multiaddr
```

## Browser `<script>` tag

Loading this module through a script tag will make its exports available as `MultiformatsUriToMultiaddr` in the global namespace.

```html
<script src="https://unpkg.com/@multiformats/uri-to-multiaddr/dist/index.min.js"></script>
```

# API Docs

- <https://multiformats.github.io/js-uri-to-multiaddr>

# License

Licensed under either of

- Apache 2.0, ([LICENSE-APACHE](https://github.com/multiformats/js-uri-to-multiaddr/LICENSE-APACHE) / <http://www.apache.org/licenses/LICENSE-2.0>)
- MIT ([LICENSE-MIT](https://github.com/multiformats/js-uri-to-multiaddr/LICENSE-MIT) / <http://opensource.org/licenses/MIT>)

# Contribution

Unless you explicitly state otherwise, any contribution intentionally submitted for inclusion in the work by you, as defined in the Apache-2.0 license, shall be dual licensed as above, without any additional terms or conditions.
