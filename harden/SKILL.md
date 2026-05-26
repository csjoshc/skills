---
name: harden
description: >-
  Security hardening for code. Use when writing or auditing code that
  handles input, secrets, uploads, or auth. OWASP examples, three-tier
  boundaries, rate limiting. Distinct from /security-review (PR-time
  review) and pr-review.
---

<!-- imported from addyosmani/agent-skills security-and-hardening -->

# Security and Hardening

Treat every external input as hostile, every secret as sacred, every authorization check as mandatory.

## When to Use

| Trigger | Note |
|---|---|
| User input handler | Validate at boundary |
| Auth / authz changes | Always ask first |
| PII / payment data | Encrypted at rest |
| External integration | Validate responses |
| File upload / webhook | Type + size limits |

## Three-Tier Boundary System

### Always Do

- Validate external input at boundaries (API routes, form handlers)
- Parameterize all DB queries — never concatenate input into SQL
- Encode output (use framework auto-escaping)
- Use HTTPS for external comms
- Hash passwords with bcrypt/scrypt/argon2
- Set security headers (CSP, HSTS, X-Frame-Options, X-Content-Type-Options)
- Use httpOnly, secure, sameSite cookies for sessions
- Run `npm audit` before each release

### Ask First (human approval)

- New auth flows or auth logic changes
- Storing new sensitive-data categories
- New external integrations
- CORS changes
- File upload handlers
- Rate limit / throttle changes
- Granting elevated permissions

### Never Do

- Commit secrets to version control
- Log sensitive data
- Trust client-side validation as security
- Disable security headers for convenience
- Use `eval()` or `innerHTML` with user data
- Store sessions in client-accessible storage
- Expose stack traces to users
- Hardcode runtime / vendor / environment names into identifiers, config filenames, or paths in code that is supposed to be agnostic — `agent.local-dmr.yaml` for a runtime-agnostic config, `OLLAMA_BASE_URL` for what should be `LLM_BASE_URL`, `"../proof/4G-ui-cycle"` for a proof root. These look cosmetic but rotate the threat surface: when defaults shift or fall-throughs hit, the wrong subsystem is reached and security assumptions (URL allow-lists, network policies, TLS bindings) silently move. Names must reflect the abstraction; vendor tokens belong in `runtime:` selector values or per-vendor adapter modules only.

## OWASP Top 10 Prevention

### 1. Injection

```typescript
// BAD
const query = `SELECT * FROM users WHERE id = '${userId}'`;

// GOOD: parameterized
const user = await db.query('SELECT * FROM users WHERE id = $1', [userId]);

// GOOD: ORM
const user = await prisma.user.findUnique({ where: { id: userId } });
```

### 2. Broken Authentication

```typescript
import { hash, compare } from 'bcrypt';

const SALT_ROUNDS = 12;
const hashedPassword = await hash(plaintext, SALT_ROUNDS);
const isValid = await compare(plaintext, hashedPassword);

app.use(session({
  secret: process.env.SESSION_SECRET,
  resave: false,
  saveUninitialized: false,
  cookie: {
    httpOnly: true,
    secure: true,
    sameSite: 'lax',
    maxAge: 24 * 60 * 60 * 1000,
  },
}));
```

### 3. XSS

```typescript
// BAD
element.innerHTML = userInput;

// GOOD
return <div>{userInput}</div>;

// If HTML required, sanitize
import DOMPurify from 'dompurify';
const clean = DOMPurify.sanitize(userInput);
```

### 4. Broken Access Control

```typescript
app.patch('/api/tasks/:id', authenticate, async (req, res) => {
  const task = await taskService.findById(req.params.id);
  if (task.ownerId !== req.user.id) {
    return res.status(403).json({
      error: { code: 'FORBIDDEN', message: 'Not authorized to modify this task' }
    });
  }
  const updated = await taskService.update(req.params.id, req.body);
  return res.json(updated);
});
```

### 5. Misconfiguration

```typescript
import helmet from 'helmet';
app.use(helmet());

app.use(helmet.contentSecurityPolicy({
  directives: {
    defaultSrc: ["'self'"],
    scriptSrc: ["'self'"],
    styleSrc: ["'self'", "'unsafe-inline'"],
    imgSrc: ["'self'", 'data:', 'https:'],
    connectSrc: ["'self'"],
  },
}));

app.use(cors({
  origin: process.env.ALLOWED_ORIGINS?.split(',') || 'http://localhost:3000',
  credentials: true,
}));
```

### 6. Sensitive Data Exposure

```typescript
function sanitizeUser(user: UserRecord): PublicUser {
  const { passwordHash, resetToken, ...publicFields } = user;
  return publicFields;
}

const API_KEY = process.env.STRIPE_API_KEY;
if (!API_KEY) throw new Error('STRIPE_API_KEY not configured');
```

## Input Validation

```typescript
import { z } from 'zod';

const CreateTaskSchema = z.object({
  title: z.string().min(1).max(200).trim(),
  description: z.string().max(2000).optional(),
  priority: z.enum(['low', 'medium', 'high']).default('medium'),
  dueDate: z.string().datetime().optional(),
});

app.post('/api/tasks', async (req, res) => {
  const result = CreateTaskSchema.safeParse(req.body);
  if (!result.success) {
    return res.status(422).json({
      error: { code: 'VALIDATION_ERROR', message: 'Invalid input', details: result.error.flatten() },
    });
  }
  const task = await taskService.create(result.data);
  return res.status(201).json(task);
});
```

### File Upload

```typescript
const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp'];
const MAX_SIZE = 5 * 1024 * 1024;

function validateUpload(file: UploadedFile) {
  if (!ALLOWED_TYPES.includes(file.mimetype)) throw new ValidationError('File type not allowed');
  if (file.size > MAX_SIZE) throw new ValidationError('File too large (max 5MB)');
  // Don't trust extension — check magic bytes if critical
}
```

## Triaging `npm audit`

| Severity | Reachable? | Action |
|---|---|---|
| Critical / High | Yes | Fix immediately |
| Critical / High | No (dev-only / unused path) | Fix soon, not blocker |
| Moderate | Production | Next release cycle |
| Moderate | Dev-only | Backlog |
| Low | Any | Regular dep updates |

If no fix exists: workarounds, replace dep, or allowlist with review date. Document deferrals.

## Rate Limiting

```typescript
import rateLimit from 'express-rate-limit';

app.use('/api/', rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100,
  standardHeaders: true,
  legacyHeaders: false,
}));

app.use('/api/auth/', rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 10,
}));
```

## Secrets Management

```
.env files:
  .env.example  → committed
  .env          → NOT committed
  .env.local    → NOT committed

.gitignore:
  .env
  .env.local
  .env.*.local
  *.pem
  *.key
```

```bash
git diff --cached | grep -i "password\|secret\|api_key\|token"
```

## Security Review Checklist

```markdown
### Authentication
- [ ] Passwords hashed with bcrypt/scrypt/argon2 (≥12 rounds)
- [ ] Session tokens httpOnly, secure, sameSite
- [ ] Login rate-limited
- [ ] Password reset tokens expire

### Authorization
- [ ] Every endpoint checks permissions
- [ ] Users access only their own resources
- [ ] Admin actions verify admin role

### Input
- [ ] All input validated at boundary
- [ ] Queries parameterized
- [ ] HTML output encoded

### Data
- [ ] No secrets in code or VCS
- [ ] Sensitive fields excluded from API responses
- [ ] PII encrypted at rest if applicable

### Infrastructure
- [ ] Security headers (CSP, HSTS, etc.)
- [ ] CORS restricted to known origins
- [ ] Deps audited
- [ ] Errors don't expose internals
```

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "Internal tool, security doesn't matter" | Internal tools get compromised. |
| "We'll add security later" | Retrofitting is 10x harder. |
| "No one would exploit this" | Automated scanners find it. |
| "Framework handles security" | Provides tools, not guarantees. |
| "It's just a prototype" | Prototypes become production. |

## Red Flags

- User input passed direct to queries, shell, or HTML
- Secrets in source / commit history
- Endpoints without auth/authz checks
- Missing CORS or wildcard origins
- No rate limiting on auth endpoints
- Stack traces exposed to users
- Critical-vuln deps
- Runtime/vendor name hardcoded into a config or path that should be agnostic (a `local-dmr.yaml` whose only DMR-specific content is `provider.base_url`; an `OLLAMA_BASE_URL` env var in a project whose surface is supposed to be `LLM_*`) — the name asserts a coupling the architecture denies, and operational defaults drift silently when the vendor swap happens
- Hardcoded artifact paths containing cycle / gate / ticket slugs (`PROOF_DIR = "../proof/4G-ui-cycle"`) — proof and evidence paths inside production code rot the moment the cycle closes and become attack-tooling debris

## Verification

- [ ] `npm audit` shows no critical/high
- [ ] No secrets in code or git history
- [ ] All input validated at boundaries
- [ ] Auth/authz on every protected endpoint
- [ ] Security headers present (check DevTools)
- [ ] Errors don't expose internals
- [ ] Rate limiting on auth endpoints

## See Also

- `/security-review` — slash command for PR-time review of pending changes
- `pr-review` — broader PR review
- `api-design` — boundary design and contracts
