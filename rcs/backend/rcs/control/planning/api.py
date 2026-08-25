"""REST API for planning profile library."""
from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from rcs.control.planning import service as plan_svc

router = APIRouter()


class ProfileCreate(BaseModel):
    name: str
    algo: str  # trapezoidal | quintic
    axes: int = 6
    vel_max: list = []
    acc_max: list = []
    created_by: str | None = None


@router.get("/planning-profiles")
async def list_profiles():
    return await plan_svc.list_profiles()


@router.post("/planning-profiles", status_code=201)
async def create_profile(body: ProfileCreate):
    return await plan_svc.create(**body.model_dump())


@router.get("/planning-profiles/{profile_id}")
async def get_profile(profile_id: str):
    p = await plan_svc.get(profile_id)
    if p is None:
        raise HTTPException(404, "profile not found")
    return p


@router.delete("/planning-profiles/{profile_id}", status_code=204)
async def delete_profile(profile_id: str):
    if not await plan_svc.delete(profile_id):
        raise HTTPException(404, "profile not found")