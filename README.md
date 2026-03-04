# mogged.tv

A private, invite-only live streaming platform — like Twitch, but for small groups who want a more intimate, controlled experience.

## What is this?

mogged.tv is a self-hosted streaming platform built for small communities. Think private watch parties, team demos, creative sessions, or just hanging out with friends — without broadcasting to the entire internet.

Streamers go live, viewers join a room, everyone chats in real time. Simple as that.

## Why?

Twitch and YouTube Live are built for massive audiences. Sometimes you just want to stream for 5-10 people without the noise, ads, algorithmic nonsense, or your content being stored on someone else's servers.

mogged.tv gives you:

- **Private streams** — only people you invite can watch
- **Full control** — self-hosted, your data stays on your infrastructure
- **Real-time chat** — built into the stream, no extra setup
- **Low cost** — runs on a single cheap server at small scale (~$10-15/mo)

## How it works

- A streamer creates a room and goes live
- Viewers get a link or invite to join
- Video, audio, and chat all happen in real time through the browser
- No downloads, no plugins, no accounts on third-party platforms

## Tech stack

- **Frontend:** React
- **Backend:** FastAPI (Python)
- **Streaming & chat:** LiveKit (self-hosted, WebRTC)
- **Database:** PostgreSQL
- **Hosting:** Any VPS (Hetzner, DigitalOcean, EC2, etc.)

## Features

### Streaming & access control

- **Multiple access levels** — public, friends-only, org-only, and invite-link-only streams
- **Organizations** — create groups, manage members with roles, restrict streams to org members
- **Friends system** — send/accept/decline friend requests, stream to friends only
- **Invite links** — generate shareable links with optional expiration and max-use limits

### Security

- **JWT authentication** — short-lived tokens with enforced secret strength (32+ chars required at startup)
- **Hardened JWT decode** — explicit signature verification and required claims (`sub`, `exp`, `iat`)
- **Timing-safe login** — constant-time password verification prevents email enumeration
- **Generic error messages** — no leaking of internal IDs, filter criteria, or field values in API responses
- **Security headers** — X-Content-Type-Options, X-Frame-Options, Strict-Transport-Security on every response
- **Restricted CORS** — explicit allow-lists for methods and headers (no wildcards)
- **Stream visibility enforcement** — all read endpoints respect access levels, not just join

### Other

- **Trivia system** — built-in trivia with categories, difficulty levels, and aura scoring
- **User profiles** — display names, avatars, stats

## Current status

Early MVP — actively being built.

## License

TBD
