from pathlib import Path


def main() -> None:
    try:
        p = Path("mcp_config_converter") / "_version.py"
        if p.exists():
            p.unlink()
    except Exception as e:
        # Best-effort removal; don't fail the build on any error here
        print(f"Could not remove _version.py: {e}")


if __name__ == "__main__":
    main()
