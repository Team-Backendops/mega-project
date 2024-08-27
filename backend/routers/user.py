from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from crud.user import get_user_by_username, create_user, verify_password

router = APIRouter()

@router.post("/login")
async def post_login(request: Request):
    try:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")

        user = get_user_by_username(username)
        if not user:
            return RedirectResponse(url="/login?message=User does not exist", status_code=status.HTTP_302_FOUND)

        if not verify_password(user['password'], password):
            return RedirectResponse(url="/login?message=Invalid password", status_code=status.HTTP_302_FOUND)

        request.session['user'] = username
        return RedirectResponse(url="/protected?message=Login successful", status_code=status.HTTP_302_FOUND)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/logout")
async def logout(request: Request):
    try:
        request.session.clear()
        return RedirectResponse(url="/login?message=You have been logged out.", status_code=status.HTTP_302_FOUND)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/register")
async def post_register(request: Request):
    try:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")
        confirm_password = form.get("confirm_password")

        if password != confirm_password:
            return RedirectResponse(url="/register?message=Passwords do not match", status_code=status.HTTP_302_FOUND)

        if not username or not password or not confirm_password:
            return RedirectResponse(url="/register?message=Please fill in all fields", status_code=status.HTTP_302_FOUND)

        create_user(username, password)
        return RedirectResponse(url="/login?message=Registration successful. Please log in.", status_code=status.HTTP_302_FOUND)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
