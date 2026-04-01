# OpenFang for ARM64 (aarch64)

This guide documents the steps required to build and run OpenFang on **ARM64 (aarch64)** environments, such as Oracle Cloud ARM instances, Raspberry Pi 5, or AWS Graviton.

## Architecture Support

Since pre-built binaries for ARM64 are currently unavailable, you must build from source. This fork includes specific patches and documentation to ensure a smooth build on ARM64 Linux.

### Prerequisites (Native Dependencies)

Before building, you must install the following system libraries (Ubuntu/Debian):

```bash
sudo apt update && sudo apt install -y \
  build-essential pkg-config libssl-dev \
  libglib2.0-dev libcairo2-dev libpango1.0-dev \
  libatk1.0-dev libgdk-pixbuf-2.0-dev libgtk-3-dev \
  libsoup-3.0-dev libwebkit2gtk-4.1-dev \
  libjavascriptcoregtk-4.1-dev libudev-dev
```

### 1. Install Rust Toolchain

Install Rust using the official installer:

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source "$HOME/.cargo/env"
```

### 2. Manual Fix for `openfang-runtime`

The current version of the `rmcp` SDK (v1.2+) introduced a `#[non_exhaustive]` attribute on transport configs. You must apply the following fix to `crates/openfang-runtime/src/mcp.rs`:

**File**: `crates/openfang-runtime/src/mcp.rs` (Lines 310-314)

Replace the struct expression:
```rust
let config = StreamableHttpClientTransportConfig {
    uri: Arc::from(url),
    custom_headers,
    ..Default::default()
};
```

With the explicit field assignment:
```rust
let mut config = StreamableHttpClientTransportConfig::default();
config.uri = Arc::from(url);
config.custom_headers = custom_headers;
```

### 3. Build from Source

```bash
cargo build --release
```

The optimized binary will be located at `target/release/openfang`.

---

## Headless / Server Setup

For cloud instances (Oracle Cloud, etc.), you should run OpenFang as a headless daemon.

### 1. Initialize
```bash
./target/release/openfang init --quick
```

### 2. Start as a Daemon
```bash
./target/release/openfang start
```

## OpenWebUI Integration

OpenFang provides a built-in **OpenAI-compatible API** on port `4200`.

To connect **OpenWebUI** to OpenFang:
1. Open your OpenWebUI instance.
2. Go to **Settings** > **Connections**.
3. Add a new **OpenAI API** connection:
   - **URL**: `http://<YOUR_SERVER_IP>:4200/v1`
   - **API Key**: (The key generated during `openfang init`)
4. Your OpenFang agents will now appear in the OpenWebUI model list.

---

## Benchmarking & Performance (ARM64 CPU-only)

Testing was performed on an Oracle Cloud **Neoverse-N1 (4 OCPUs, 24GB RAM)** architecture.

| Model | System Prompt | Status | Latency (TTFT) |
| :--- | :--- | :--- | :--- |
| **Llama 3.2 3B** | Full (2,000 tokens) | ❌ **FAIL** | > 120s (Timeout) |
| **Llama 3.2 3B** | Slim (300 tokens) | ❌ **FAIL** | > 120s (Timeout) |
| **Llama 3.1 8B** | Slim (300 tokens) | ❌ **FAIL** | > 120s (Timeout) |

### ⚠️ Findings: The Hardware "Wall"
On CPU-only ARM instances, the **Prompt Evaluation (Prefill)** stage is the primary bottleneck. 
*   Even with a minimal 300-token prompt, the 4-core CPU takes **over 2 minutes** to pre-process the context before generating the first token. 
*   This causes "heartbeat" timeouts and "Agent unresponsive" errors in the OpenFang Kernel.

### 🌟 Ultimate Recommendation: Hybrid Mode
For a smooth experience on ARM64 cloud instances, we recommend **Hybrid Mode**:
1.  **Kernel**: Run the OpenFang **Kernel** and local tools on your ARM server (highly efficient).
2.  **LLM**: Connect an external **OpenAI-compatible API** (e.g., **Google Gemini 1.5 Flash**, **Groq**, or **OpenRouter**).

This enables sub-second response times while keeping your agents and data control on your own ARM instance.

---

*This ARM64 optimization and benchmarking was performed on `2026-04-01`.*


