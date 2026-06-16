from http import HTTPStatus

from groq_client import interpret_dream


def handler(request):
    """Vercel serverless interpretation endpoint backed by Groq."""
    try:
        body = request.get_json(silent=True) or {}
        dream = (body.get("dream") or "").strip()
        db_context = (body.get("db_context") or "").strip()

        if not dream:
            return ({"success": False, "message": "No dream provided"}, HTTPStatus.BAD_REQUEST)

        result = interpret_dream(dream, db_context=db_context)
        if result["success"]:
            return (
                {
                    "success": True,
                    "dream": dream,
                    "interpretation": result["interpretation"],
                    "meta": {"method": "groq", "model": result["model"]},
                },
                HTTPStatus.OK,
            )

        return (
            {
                "success": False,
                "dream": dream,
                "interpretation": "",
                "meta": {"method": "groq", "model": result["model"]},
                "message": result["error"],
            },
            HTTPStatus.BAD_GATEWAY,
        )
    except Exception as e:
        return ({"success": False, "message": str(e)}, HTTPStatus.INTERNAL_SERVER_ERROR)
