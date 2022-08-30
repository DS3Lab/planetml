import typer
import requests

planetml_url = 'https://planetd.shift.ml/jobs'

agent = typer.Typer()

@agent.command()
def fetch():
    """
    Fetch jobs
    """
    response = requests.get(planetml_url)
    print(response.text)

if __name__=="__main__":
    agent()
