from emmett55 import App, request, response
from jinja2 import Environment, PackageLoader, select_autoescape


app = App(__name__)
templates = Environment(loader=PackageLoader(__name__), autoescape=select_autoescape())


@app.route("/")
async def index():
    response.content_type = "text/html; charset=utf-8"
    name = request.query_params.name or "traveler"
    return templates.get_template("index.html").render(name=name)
