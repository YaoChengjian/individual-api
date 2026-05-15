import os
import platform
import socket
import subprocess
import sys


def ensure_native_arm64():
    """
    在 Apple Silicon 机器上，如果当前 Python 进程是 x86_64，
    则自动重启为 arm64，避免加载 arm64 扩展包时报架构错误。
    """

    if os.getenv("RUNPY_ARM64_REEXEC") == "1":
        return

    process_arch = platform.machine()
    if process_arch != "x86_64":
        return

    try:
        host_supports_arm64 = (
            subprocess.check_output(["sysctl", "-in", "hw.optional.arm64"], text=True).strip() == "1"
        )
    except Exception:
        host_supports_arm64 = False

    if not host_supports_arm64:
        return

    env = os.environ.copy()
    env["RUNPY_ARM64_REEXEC"] = "1"
    os.execvpe("arch", ["arch", "-arm64", sys.executable, *sys.argv], env)


def is_port_available(host: str, port: int) -> bool:
    """Check whether the target port can be bound on the current host."""

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((host, port))
        except OSError:
            return False
    return True


def find_available_port(host: str, preferred_port: int, scan_count: int) -> int:
    """Return the first available port starting from the preferred port."""

    for port in range(preferred_port, preferred_port + scan_count):
        if is_port_available(host, port):
            return port
    raise RuntimeError(
        f"Unable to find an available port in range "
        f"{preferred_port}-{preferred_port + scan_count - 1}"
    )


def main():
    ensure_native_arm64()
    host = os.getenv("HOST", "0.0.0.0")
    preferred_port = int(os.getenv("PORT", "18000"))
    reload_enabled = os.getenv("UVICORN_RELOAD", "0") == "1"
    port_scan_count = int(os.getenv("PORT_SCAN_COUNT", "20"))
    actual_port = find_available_port(host, preferred_port, port_scan_count)

    if actual_port != preferred_port:
        print(f"Port {preferred_port} is in use, automatically switched to {actual_port}.")

    # Keep docs/openapi server metadata aligned with the actual runtime port.
    os.environ["PORT"] = str(actual_port)
    os.environ["BASE_HOST"] = f"http://127.0.0.1:{actual_port}"

    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=host,
        port=actual_port,
        reload=reload_enabled,
    )


if __name__ == "__main__":
    main()
