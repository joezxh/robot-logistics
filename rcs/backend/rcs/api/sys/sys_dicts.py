"""Dictionary endpoints (``/api/sys/dictionaries``).

``sys_dictionary`` groups ``sys_dictionary_item`` rows by ``dict_code``. The
console front-end caches them after login and uses them to render status tags,
selects and colour chips.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from rcs.services.sys.sys_deps import get_current_user, get_db, require_permissions
from rcs.db.sys_models import SysDictionary, SysDictionaryItem
from rcs.services.sys.sys_schemas import (
    DictCreate,
    DictItemCreate,
    DictItemRow,
    DictItemUpdate,
    DictRow,
    DictUpdate,
    DictWithItems,
    Envelope,
)
from rcs.services.sys.sys_service import (
    create_dictionary,
    create_dictionary_item,
    delete_dictionary,
    delete_dictionary_item,
    get_dictionaries_batch,
    get_dictionary_with_items,
    list_dictionaries,
    list_dictionary_items,
    update_dictionary,
    update_dictionary_item,
)

router = APIRouter(prefix="/dictionaries", tags=["sys-dicts"])


async def _get_dict_or_404(db: AsyncSession, dict_code: str) -> SysDictionary:
    d = (
        await db.execute(
            select(SysDictionary).where(
                SysDictionary.dict_code == dict_code, SysDictionary.is_deleted.is_(False)
            )
        )
    ).scalar_one_or_none()
    if d is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="字典不存在")
    return d


async def _get_item_or_404(db: AsyncSession, item_id: int) -> SysDictionaryItem:
    item = await db.get(SysDictionaryItem, item_id)
    if item is None or item.is_deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="字典项不存在")
    return item


# --- Dictionary level ------------------------------------------------------

@router.get("", response_model=Envelope[list[DictRow]])
async def get_dictionaries(
    keyword: str | None = Query(None),
    dict_type: str | None = Query(None, alias="type"),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
) -> Envelope[list[DictRow]]:
    """List dictionaries (readable by any authenticated user)."""
    rows = await list_dictionaries(db, keyword=keyword, dict_type=dict_type)
    return Envelope(data=rows, total=len(rows))


@router.get("/batch", response_model=Envelope[dict])
async def get_dictionaries_batch_endpoint(
    codes: str = Query(..., description="逗号分隔的字典编码，如 user_status,menu_type"),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
) -> Envelope[dict]:
    """Fetch several dictionaries at once — used on console bootstrap."""
    code_list = [c.strip() for c in codes.split(",") if c.strip()]
    grouped = await get_dictionaries_batch(db, code_list)
    return Envelope(data={k: [i.model_dump() for i in v] for k, v in grouped.items()})


@router.get("/{dict_code}", response_model=Envelope[DictWithItems])
async def get_dictionary(
    dict_code: str,
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
) -> Envelope[DictWithItems]:
    """Dictionary together with its items."""
    result = await get_dictionary_with_items(db, dict_code)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="字典不存在")
    return Envelope(data=result)


@router.post(
    "",
    response_model=Envelope[DictRow],
    dependencies=[Depends(require_permissions("sys:dict:create"))],
)
async def post_dictionary(
    payload: DictCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
) -> Envelope[DictRow]:
    """Create a dictionary, optionally with its initial items."""
    existing = (
        await db.execute(
            select(SysDictionary).where(SysDictionary.dict_code == payload.dictCode)
        )
    ).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="字典编码已存在")

    body = payload.model_dump()
    created = await create_dictionary(db, body, created_by=current_user.user_id)
    rows = await list_dictionaries(db, keyword=created.dict_code)
    return Envelope(message="创建成功", data=next(r for r in rows if r.dictId == created.dict_id))


@router.put(
    "/{dict_code}",
    response_model=Envelope[DictRow],
    dependencies=[Depends(require_permissions("sys:dict:update"))],
)
async def put_dictionary(
    dict_code: str,
    payload: DictUpdate,
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
) -> Envelope[DictRow]:
    """Update dictionary metadata (``dict_code`` itself is the key, not editable)."""
    d = await _get_dict_or_404(db, dict_code)
    updated = await update_dictionary(db, d, payload.model_dump(exclude_none=True))
    rows = await list_dictionaries(db, keyword=updated.dict_code)
    return Envelope(message="更新成功", data=next(r for r in rows if r.dictId == updated.dict_id))


@router.delete(
    "/{dict_code}",
    dependencies=[Depends(require_permissions("sys:dict:delete"))],
)
async def remove_dictionary(
    dict_code: str,
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
) -> Envelope[None]:
    """Soft-delete a dictionary and purge its items."""
    d = await _get_dict_or_404(db, dict_code)
    await delete_dictionary(db, d)
    return Envelope(message="删除成功")


# --- Item level ------------------------------------------------------------

@router.get("/{dict_code}/items", response_model=Envelope[list[DictItemRow]])
async def get_items(
    dict_code: str,
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
) -> Envelope[list[DictItemRow]]:
    """Items of one dictionary, ordered by ``sort_order``."""
    await _get_dict_or_404(db, dict_code)
    rows = await list_dictionary_items(db, dict_code)
    return Envelope(data=rows, total=len(rows))


@router.post(
    "/{dict_code}/items",
    response_model=Envelope[DictItemRow],
    dependencies=[Depends(require_permissions("sys:dict:create"))],
)
async def post_item(
    dict_code: str,
    payload: DictItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
) -> Envelope[DictItemRow]:
    """Append an item to a dictionary."""
    await _get_dict_or_404(db, dict_code)
    body = payload.model_dump()
    body["dictCode"] = dict_code

    clash = (
        await db.execute(
            select(SysDictionaryItem).where(
                SysDictionaryItem.dict_code == dict_code,
                SysDictionaryItem.item_code == payload.itemCode,
                SysDictionaryItem.is_deleted.is_(False),
            )
        )
    ).scalar_one_or_none()
    if clash is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="字典项编码已存在")

    item = await create_dictionary_item(db, body, created_by=current_user.user_id)
    from rcs.services.sys.sys_service import _item_to_row

    return Envelope(message="创建成功", data=_item_to_row(item))


@router.put(
    "/items/{item_id}",
    response_model=Envelope[DictItemRow],
    dependencies=[Depends(require_permissions("sys:dict:update"))],
)
async def put_item(
    item_id: int,
    payload: DictItemUpdate,
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
) -> Envelope[DictItemRow]:
    """Update a dictionary item."""
    item = await _get_item_or_404(db, item_id)
    updated = await update_dictionary_item(db, item, payload.model_dump(exclude_none=True))
    from rcs.services.sys.sys_service import _item_to_row

    return Envelope(message="更新成功", data=_item_to_row(updated))


@router.delete(
    "/items/{item_id}",
    dependencies=[Depends(require_permissions("sys:dict:delete"))],
)
async def remove_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
) -> Envelope[None]:
    """Soft-delete a dictionary item."""
    item = await _get_item_or_404(db, item_id)
    await delete_dictionary_item(db, item)
    return Envelope(message="删除成功")
