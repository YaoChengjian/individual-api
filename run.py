import os
import platform
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


def main():
    ensure_native_arm64()

    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "18000")),
        reload=os.getenv("UVICORN_RELOAD", "0") == "1",
    )


if __name__ == "__main__":
    main()
