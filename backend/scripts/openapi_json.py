import json


def main() -> None:
    from app.build import create_app

    with open("openapi.json", "w") as f:
        f.write(json.dumps(create_app().openapi(), indent=2))
    print("openapi.json has been generated")


if __name__ == "__main__":
    main()
