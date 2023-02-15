# Celtic Tuning

Unofficial Celtic Tuning API, (very) basic web app, and CLI tool.

## Usage

```shell
pip install -r requirements.txt
flask --app celtic_web run
```

Browse to <http://localhost:5000> and use the web interface or query from CLI like so:

`curl -sG 'localhost:5000/get_vehicle' -d vrn=ab12cde`

### Docker

A Dockerfile is included. Usage:

```
docker build . -tag celtictuning
docker run -p 5000:5000 celtictuning
```

### Local CLI

You can also use the local CLI tool to query without running the Flask app:

```
python3 celtic_cli.py ab12cde
```

## Disclaimer

I am in no way affiliated with or endorsed by Celtic Tuning.

This project functions by scraping the Celtic Tuning web page, so it's about as far from official as you can get.

This project should not be used in any official capacity, it is offered “as-is”, without warranty, and I accept no liability for damages resulting from using the project.
