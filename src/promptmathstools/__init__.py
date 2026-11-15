def main() -> None:
    print("\n [main()] started")
    try:
        print("Hello from promptmathstools!")
    except Exception as error:
        print(f"\n [main()] error: {error!r}")
        raise
    finally:
        print("\n [main()] ended")
