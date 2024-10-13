# Emmett55

Emmett55 is a Python micro web framework designed with simplicity in mind.

```python
from emmett55 import App, request, response
from emmett55.tools import service, requires

app = App(__name__)

def is_authenticated():
    return request.headers.get("api-key") == "foobar"
    
def not_authorized():
    response.status = 401
    return {"error": "not authorized"}

@app.route("/", methods='get')
@requires(is_authenticated, otherwise=not_authorized)
@service.json
async def index():
    return {"message": "hello world"}
```

## Compared with Emmett

Emmett55 is based on [Emmett](https://emmett.sh) and shares the following features with it:

- [application and modules](https://emmett.sh/docs/latest/app_and_modules)
- [routing](https://emmett.sh/docs/latest/routing)
- [request](https://emmett.sh/docs/latest/request)/[response](https://emmett.sh/docs/latest/response)/[session](https://emmett.sh/docs/latest/sessions)/[websocket](https://emmett.sh/docs/latest/websocket) helpers
- the [pipeline](https://emmett.sh/docs/latest/pipeline)
- [services](https://emmett.sh/docs/latest/services) (JSON only)
- [caching](https://emmett.sh/docs/latest/caching) (except for disk cache)
- [HTML](https://emmett.sh/docs/latest/html) code generation
- [extensions](https://emmett.sh/docs/latest/extensions)
- [testing client](https://emmett.sh/docs/latest/testing)
- CLI (with the `emmett55` command)

Consequentially, Emmett55 doesn't include:

- the [ORM](https://emmett.sh/docs/latest/orm)
- the [authentication system](https://emmett.sh/docs/latest/auth)
- the [templating system](https://emmett.sh/docs/latest/templates)
- the [internationalization system](https://emmett.sh/docs/latest/languages)
- [validations](https://emmett.sh/docs/latest/validations)
- [forms](https://emmett.sh/docs/latest/forms) utilities
- XML services
- disk caching
- the [mailer](https://emmett.sh/docs/latest/mailer)
- the [debugger](https://emmett.sh/docs/latest/debug_and_logging#debugger)

Typical use-cases for picking Emmett55 over Emmett are:

- the lack of need of the upper-mentioned missing features
- the desire to use different libraries in place of the Emmett components, like SQLAlchemy or Jinja

## Documentation

While we're still in the process of developing Emmett55 documentation, the [Emmett one](https://emmett.sh/docs) can be examined – with the caviat to replace `emmett` with `emmett55` when mentioned and keep in mind the upper-mentioned list of non-included features.

## License

Emmett55 is released under the BSD License.
