from app.http import HttpRequest, HttpResponse, HttpStatus
import pathlib


def handle_req(req: HttpRequest, directory: str | None) -> HttpResponse:
    match req.urlpath.path:
        case "":
            res = HttpResponse.empty(status=HttpStatus.Ok200)

        case "user-agent":
            user_agent = req.headers.get("User-Agent", "")
            res = HttpResponse.text_content(status=HttpStatus.Ok200, content=user_agent)

        case x if x.startswith("echo/"):
            res = HttpResponse.text_content(status=HttpStatus.Ok200, content=x[5:])
        case x if x.startswith("files/"):
            if not directory:
                res = HttpResponse.empty(status=HttpStatus.NotFound404)
            else:
                filename = x[6:]
                dirpath = pathlib.Path(directory)
                filepath = dirpath / filename
                if filepath.exists():
                    with open(filepath, "r") as f:
                        content = f.read()
                    res = HttpResponse.text_content(
                        status=HttpStatus.Ok200, content=content
                    )
                else:
                    res = HttpResponse.empty(status=HttpStatus.NotFound404)

        case _:
            res = HttpResponse.empty(status=HttpStatus.NotFound404)
    return res
