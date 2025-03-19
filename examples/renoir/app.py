from emmett55 import App, request
from emmett55.templating import AbstractTemplater
from renoir import Renoir


class Templates(AbstractTemplater):
    def on_load(self):
        super().on_load()
        self.templater = Renoir(path=self.config.path)

    def render(self, template, ctx):
        return self.templater.render(template, ctx)


app = App(__name__)
templates = app.use_extension(Templates)


@app.route("/")
@templates()
async def index():
    name = request.query_params.name or "traveler"
    return {"name": name}


@app.route()
@templates(name="index.html")
async def scream():
    name = request.query_params.name or "traveler"
    return {"name": name.upper()}
