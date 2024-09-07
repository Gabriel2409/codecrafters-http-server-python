from app.http import HttpMethod, HttpRequest, HttpResponse, HttpStatus
import pathlib


def handle_req(req: HttpRequest, directory: str | None) -> HttpResponse:
    match req.method:
        case HttpMethod.GET:
            return handle_get_req(req, directory)
        case HttpMethod.POST:
            return handle_post_req(req, directory)
        case _:
            return HttpResponse.empty(status=HttpStatus.NotFound404)


def handle_get_req(req: HttpRequest, directory: str | None) -> HttpResponse:
    accepted_encodings = req.headers.get("Accept-Encoding", "").split(", ")

    if "gzip" in accepted_encodings:
        content_encoding = "gzip"
    else:
        content_encoding = None

    match req.urlpath.path:
        case "":
            res = HttpResponse.empty(status=HttpStatus.Ok200)

        case "user-agent":
            user_agent = req.headers.get("User-Agent", "")
            res = HttpResponse.text_content(
                status=HttpStatus.Ok200,
                content=user_agent,
                content_encoding=content_encoding,
            )

        case x if x.startswith("echo/"):
            res = HttpResponse.text_content(
                status=HttpStatus.Ok200,
                content=x[5:],
                content_encoding=content_encoding,
            )
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
                        status=HttpStatus.Ok200,
                        content=content,
                        content_type="application/octet-stream",
                        content_encoding=content_encoding,
                    )
                else:
                    res = HttpResponse.empty(status=HttpStatus.NotFound404)

        case _:
            res = HttpResponse.empty(status=HttpStatus.NotFound404)
    return res


def handle_post_req(req: HttpRequest, directory: str | None) -> HttpResponse:
    match req.urlpath.path:
        case x if x.startswith("files/"):
            if not directory:
                res = HttpResponse.empty(status=HttpStatus.NotFound404)
            else:
                filename = x[6:]
                dirpath = pathlib.Path(directory)
                filepath = dirpath / filename
                if filepath.exists():
                    res = HttpResponse.empty(status=HttpStatus.Conflict409)
                else:
                    with open(filepath, "w") as f:
                        f.write(req.body)

                    res = HttpResponse.empty(status=HttpStatus.Created201)

        case _:
            res = HttpResponse.empty(status=HttpStatus.NotFound404)
    return res
