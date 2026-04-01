feat: install OpenFang on aarch64 (headless)

Problem:
- Missing pre-built binaries for ARM64 architecture.
- Missing system build dependencies (glib, libsoup, webkit2gtk, udev).
- Code incompatibility in 'openfang-runtime' with non-exhaustive struct 'StreamableHttpClientTransportConfig' from 'rmcp' SDK.

Solution:
- Installed Rust toolchain and system dependencies for ARM64 compilation.
- Patched 'crates/openfang-runtime/src/mcp.rs' to avoid struct expressions for non-exhaustive library config, ensuring compatibility with the latest SDK.
- Compiled and optimized the repository from source.
- Set up headless daemon service for Oracle Cloud ARM instance.
