from src.app.app import App
import requests


def main() -> None:
    session = requests.Session()
    app = App(session)
    app.run()

if __name__ == '__main__':
    main()
