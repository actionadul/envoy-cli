# envoy-cli

> A CLI tool to manage and diff environment variable sets across multiple deployment targets.

---

## Installation

```bash
pip install envoy-cli
```

Or install from source:

```bash
git clone https://github.com/yourname/envoy-cli.git && cd envoy-cli && pip install .
```

---

## Usage

Define your environment sets in a YAML config file, then use `envoy` to inspect, compare, and sync them across targets.

```bash
# List all configured deployment targets
envoy targets list

# Show environment variables for a specific target
envoy env show --target production

# Diff environment variables between two targets
envoy env diff --from staging --to production

# Set a variable on a target
envoy env set MY_API_KEY=abc123 --target staging
```

**Example `envoy.yaml`:**

```yaml
targets:
  staging:
    source: .env.staging
  production:
    source: .env.production
```

---

## Features

- Compare env vars across multiple deployment targets side by side
- Detect missing, extra, or mismatched variables between environments
- Supports `.env` files and YAML-based configuration
- Simple, scriptable CLI interface

---

## License

MIT © [yourname](https://github.com/yourname)