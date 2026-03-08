# Why Version APIs?

## Why This Matters

Imagine you're maintaining an iOS app. You ship v1.0 with a screen that displays user profiles fetched from your API. The API returns:

```json
{"id": 1, "name": "Alice", "email": "alice@example.com"}
```

Your app accesses `response["name"]` to display the user's name. It works perfectly.

Now your backend team decides to restructure the response:

```json
{"data": {"id": 1, "full_name": "Alice Smith", "contact": {"email": "alice@example.com"}}}
```

They deploy this change on Friday evening. What happens?

Every user running your app sees a crash. `response["name"]` is now `nil`. The App Store version can't be updated instantly -- Apple review takes 24-48 hours. Your users are stuck with a broken app until the update ships.

**This is why APIs need versioning.** The old format must continue working while the new format is introduced.

## The API Contract

An API is a contract between the server and its clients. Like any contract, both sides agree on the terms:

- **The server promises:** "When you call `GET /users/1`, I'll return `{"id": 1, "name": "Alice"}`"
- **The client expects:** "`response["name"]` will always be a string"

Breaking this contract without warning is like changing the terms of a legal agreement without notifying the other party. API versioning is how you introduce new terms while honoring the old ones.

**Mobile analogy:** Apple's iOS SDK is versioned. When they deprecated `UIWebView` in favor of `WKWebView`, they didn't remove `UIWebView` overnight. They deprecated it in iOS 12, warned developers for years, and eventually removed it. Your API should follow the same pattern.

## What Is a Breaking Change?

A **breaking change** is any change that can cause existing clients to malfunction:

| Change | Breaking? | Why |
|--------|-----------|-----|
| Remove a response field | YES | Client accessing that field gets null/crash |
| Rename a response field | YES | Same as removing (old name is gone) |
| Change a field's type (string to int) | YES | Client parsing code breaks |
| Remove an endpoint | YES | Client gets 404 |
| Change a required parameter | YES | Client's existing requests fail |
| Add an optional response field | NO | Clients that don't know about it just ignore it |
| Add a new endpoint | NO | Existing clients never call it |
| Add an optional query parameter | NO | Existing requests still work without it |
| Improve performance | NO | Response is the same, just faster |
| Fix a bug | MAYBE | Depends on whether clients rely on the buggy behavior |

**The rule:** If existing client code can break, it's a breaking change. If existing code continues working unchanged, it's non-breaking.

## When to Version

**Version when you have breaking changes that must ship.** Not before.

Common mistakes:

| Mistake | Why It's Wrong |
|---------|---------------|
| Versioning for every change | Creates unnecessary complexity; most changes are non-breaking |
| Versioning for bug fixes | Bug fixes should be backward-compatible (fix the bug, don't change the contract) |
| Versioning for adding optional fields | Adding a field is non-breaking; clients ignore unknown fields |
| Not versioning at all | Eventually you'll need a breaking change and have no path forward |

**Good reasons to create a new API version:**
- Restructuring the response format (flat to nested, renaming fields)
- Changing authentication mechanism
- Removing deprecated fields that clients relied on
- Changing pagination format
- Switching from one data model to another

## Versioning Strategies

There are two main approaches to API versioning:

### 1. URL Path Versioning

```
GET /v1/users/1  --> Returns v1 format
GET /v2/users/1  --> Returns v2 format
```

**Pros:** Explicit, easy to understand, easy to route, visible in documentation.
**Cons:** URLs change between versions.

### 2. Header Versioning

```
GET /users/1
X-API-Version: 1.0  --> Returns v1 format

GET /users/1
X-API-Version: 2.0  --> Returns v2 format
```

**Pros:** Clean URLs, single endpoint.
**Cons:** Less discoverable, harder to test in a browser, version is hidden in headers.

### Which to Choose?

**Start with URL path versioning.** It's the most explicit, most widely used, and easiest to understand. Every major API (GitHub, Stripe, Twitter) uses URL versioning.

Use header versioning only when you have a specific reason (e.g., you can't change URLs due to existing infrastructure).

## The Cost of Not Versioning

Real-world example: You build a mobile app and a backend API. Everything works. Then:

1. **Month 3:** You need to restructure user profiles. Without versioning, you either:
   - Break all existing mobile apps (bad)
   - Can't ship the improvement (also bad)

2. **Month 6:** You acquire a partner who integrates with your API. Now two clients depend on the format. Breaking changes affect both.

3. **Month 12:** Three mobile apps, two partner integrations, and a web app all depend on your API. A format change without versioning would break everything simultaneously.

**Versioning costs a little upfront but saves a lot long-term.** The overhead of maintaining two routers is far less than the cost of a production outage.

## Semantic Versioning for APIs

While not always required, you can apply semantic versioning principles:

- **Major version (v1 -> v2):** Breaking changes. New URL prefix.
- **Minor version:** New features, non-breaking. No URL change needed.
- **Patch version:** Bug fixes. No URL change needed.

In practice, most APIs only version on major changes (`/v1`, `/v2`). Minor and patch versions are communicated through documentation, not URL changes.

## Key Takeaways

1. **An API is a contract.** Don't break it without warning and a migration path.
2. **Only version for breaking changes.** Adding optional fields, new endpoints, or performance improvements don't need a new version.
3. **URL path versioning is the default choice.** It's explicit, widely understood, and easy to implement in FastAPI.
4. **The cost of versioning is low.** Two routers with shared business logic is much cheaper than broken production clients.
5. **Plan for versioning from day one.** Even if you start with only v1, structure your code so adding v2 later is straightforward.
6. **Mobile developers already understand this.** Deployment targets and `minSdkVersion` are the same concept -- supporting old clients while introducing new features.
