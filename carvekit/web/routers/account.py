
from carvekit.web.responses.api import error_dict
from carvekit.web.routers.router import api_router
from starlette.responses import JSONResponse
from typing import Union
from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session
from carvekit.web.handlers.response import Authenticate
from carvekit.web.schemas import AccountSchema, AccountSubscriptionSchema
from carvekit.web.database.managers import DBSingleton, DbFacade


@api_router.get("/account")
def account(auth: str = Depends(Authenticate), db_manager: DbFacade = Depends(DBSingleton().get_manager),
            x_api_key: Union[str, None] = Header(None)):
    if not auth:
        return JSONResponse(
            content=error_dict("Authentication failed"), status_code=403
        )
    try:
        with db_manager.get_session() as session:
            personal = db_manager.accounts.calculate_personal_credits(x_api_key)
            subscription = db_manager.subscriptions.calculate_subscription_credits_by_token(x_api_key)
            enterpice = 0 # TODO
            total = personal + subscription + enterpice
    except Exception as e:
        return JSONResponse(
            content=error_dict(str(e)), status_code=500
        )
    return JSONResponse(
        content={
            "data": {
                "attributes": {
                    "credits": {
                        "total": total,
                        "subscription": subscription,
                        "personal": personal,
                        "enterprise": enterpice,
                    },
                    "api": {"free_calls": 99999, "sizes": "all"},
                }
            }
        },
        status_code=200,
    )



# @api_router.get("/account")
# def get_account(auth: str = Depends(Authenticate), x_api_key: Union[str, None] = Header(None), session: Session = Depends(db_manager.get_session)):
#     if not auth:
#         raise HTTPException(status_code=403, detail="Authentication failed")
#     account = db_manager.accounts.get_account_by_token(x_api_key, db)
#     if not account:
#         raise HTTPException(status_code=404, detail="Account not found")
#     return account

@api_router.post("/account")
def create_account(account_data: AccountSchema, db_manager: DbFacade = Depends(DBSingleton().get_manager)):
        return db_manager.accounts.create_account_from_pydantic(account_data)

@api_router.put("/account/{token}")
def update_account(token: str, account_data: AccountSchema, db_manager: DbFacade = Depends(DBSingleton().get_manager)):
    with db_manager.get_session() as session:
        account = db_manager.accounts.get_account_by_token(token, session)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        return db_manager.accounts.update_account_from_pydantic(account_data, session)

@api_router.delete("/account/{token}")
def delete_account(token: str,  db_manager: DbFacade = Depends(DBSingleton().get_manager)):
    with db_manager.get_session() as session:
        account = db_manager.accounts.get_account_by_token(token, session)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        db_manager.accounts.delete_account_by_id(token, session)
        return {"message": "Account deleted successfully"}

@api_router.post("/account/reserve")
def reserve_credits(user_id: int, credits: int, credits_type: str,  db_manager: DbFacade = Depends(DBSingleton().get_manager)):
    with db_manager.get_session() as session:
        return db_manager.accounts.reserve_credits(user_id, credits, credits_type, session)

@api_router.post("/account/cancel-reservation/{reservation_id}")
def cancel_reservation(reservation_id: int,  db_manager: DbFacade = Depends(DBSingleton().get_manager)):
    with db_manager.get_session() as session:
        db_manager.accounts.cancel_reservation_by_id(reservation_id, session)
        return {"message": "Reservation cancelled successfully"}
