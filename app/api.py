from app.http import HttpRequest, HttpResponse, HttpStatus


def handle_req(req: HttpRequest) -> HttpResponse:
    match req.urlpath.path:
        case "":
            res = HttpResponse.empty(status=HttpStatus.Ok200)

        case "user-agent":
            user_agent = req.headers.get("User-Agent", "")
            res = HttpResponse.text_content(status=HttpStatus.Ok200, content=user_agent)

        case x if x.startswith("echo/"):
            res = HttpResponse.text_content(status=HttpStatus.Ok200, content=x[5:])
        case _:
            res = HttpResponse.empty(status=HttpStatus.NotFound404)
    return res
